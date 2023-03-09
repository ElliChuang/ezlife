from mysql.connector import errorcode
import mysql.connector 
from model.db import MySQL


class SettleModel():
    def get_overview(bookId, start_dt, end_dt, status):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        SELECT 
                            m.id, 
                            m.name, 
                            sum(p.payable) as payable,
                            sum(p.prepaid) as prepaid
                        FROM journal_list_price as p
                        INNER JOIN journal_list as j on j.id = p.journal_list_id
                        INNER JOIN member as m on m.id = p.member_id
                        INNER JOIN status as s ON j.id = s.journal_list_id
                        WHERE 	
                            j.book_id = %s 
                            AND j.date >= %s 
                            AND j.date < %s
                            AND s.status = %s
                        group by
                            m.id;
                    """)
            mycursor.execute(query, (bookId, start_dt, end_dt, status))
            overview = mycursor.fetchall()
            if overview:
                return overview
            else:
                return None
            
        except mysql.connector.Error as err:
                print("Something went wrong when get overview: {}".format(err))
                return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

    def get_journal_lists(bookId, start_dt, end_dt, status, collaborator_id):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query_basic = ("""
                            SELECT 
                                s.journal_list_id, 
                                m.id, 
                                m.name, 
                                p.payable, 
                                s.status, 
                                j.date, 
                                SUM(p.payable) OVER (PARTITION BY m.id) AS total_payable,
                                c1.name as category_main,
                                c2.name as category_object,
                                c3.name as category_character,
                                k.content as keyword
                            FROM journal_list_price as p
                            INNER JOIN journal_list as j on j.id = p.journal_list_id
                            INNER JOIN member as m on m.id = p.member_id
                            INNER JOIN journal_list_category jc1 ON j.id = jc1.journal_list_id
                            INNER JOIN categories c1 ON jc1.categories_id = c1.id AND c1.parent_category_id = 1
                            INNER JOIN journal_list_category jc2 ON j.id = jc2.journal_list_id
                            INNER JOIN categories c2 ON jc2.categories_id = c2.id AND c2.parent_category_id = 2
                            INNER JOIN journal_list_category jc3 ON j.id = jc3.journal_list_id
                            INNER JOIN categories c3 ON jc3.categories_id = c3.id AND c3.parent_category_id = 3
                            INNER JOIN journal_list_keyword jk ON j.id = jk.journal_list_id
                            LEFT JOIN keyword k ON jk.keyword_id = k.id 
                            INNER JOIN status as s ON j.id = s.journal_list_id
                            WHERE 
                                j.book_id = %s 
                                AND j.date >= %s 
                                AND j.date < %s
                                AND s.status = %s    
                        """)
            query_end = "Order by j.date DESC, j.id DESC;"
            value = (bookId, start_dt, end_dt, status)
            condition = []
            if collaborator_id:
                condition.append("m.id = %s")
            if condition:
                query_basic += " AND " + " AND ".join(condition)
                value = (bookId, start_dt, end_dt, status, collaborator_id)
            
            query = (query_basic+ " " + query_end)
            mycursor.execute(query, value)
            results = mycursor.fetchall()
            if results:
                 return results
            else:
                 return None

        except mysql.connector.Error as err:
                print("Something went wrong when get journal lists: {}".format(err))
                return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    def settle_account(bookId, start_dt, end_dt, member_id, account_dt):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            mycursor.execute("START TRANSACTION")
            query = ("""
                        SELECT s.journal_list_id
                        FROM status s
                        INNER JOIN journal_list j ON j.id = s.journal_list_id
                        WHERE 
                            j.book_id = %s 
                            AND j.date >= %s 
                            AND j.date < %s
                            AND s.status = %s    
                    """)
            value = (bookId, start_dt, end_dt, "未結算")
            mycursor.execute(query, value)
            results = mycursor.fetchall()
            if not results:
                return None

            value = []
            for item in results:
                value.append(("已結算", member_id, account_dt, item["journal_list_id"]))

            mycursor.executemany("""
                                    UPDATE status 
                                    SET status = %s, account_member_id = %s, account_dt = %s
                                    WHERE journal_list_id = %s
                                """, value)
            mycursor.execute("COMMIT")
            return "SUCCESS"
        
        except mysql.connector.Error as err:
            print("Something went wrong when settling account: {}".format(err))
            mycursor.execute("ROLLBACK")
            return "INTERNAL_SERVER_ERROR"

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close() 


    def get_records(bookId, account_dt, status):
        try:
            connection_object = MySQL.conn_obj()
            mycursor = connection_object.cursor(dictionary=True)
            query_basic = ("""
                            SELECT 
                                m.name, 
                                sum(p.payable) as payable,
                                sum(p.prepaid) as prepaid,
                                s.account_dt,
                                m2.name as account_member
                            FROM journal_list_price as p
                            INNER JOIN journal_list as j on j.id = p.journal_list_id
                            INNER JOIN member as m on m.id = p.member_id
                            INNER JOIN status as s ON j.id = s.journal_list_id
                            INNER JOIN member as m2 ON m2.id = s.account_member_id
                            WHERE 	
                                j.book_id = %s 
                                AND s.status = %s  
                        """)
            query_end = ("""
                            group by
                                s.account_dt,
                                s.account_member_id,
                                m.name
                            order by 
                                s.account_dt DESC,
                                m.name;
                        """)

            value = (bookId, status)
            if account_dt:
                query_basic += " AND s.account_dt = %s"
                value += (account_dt,)

            query = query_basic + query_end
            mycursor.execute(query, value)
            results = mycursor.fetchall()
            if results:
                return results
            else:
                return None
        
        except mysql.connector.Error as err:
                print("Something went wrong when getting records: {}".format(err))
                return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


