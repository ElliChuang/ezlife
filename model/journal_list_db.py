from mysql.connector import errorcode
import mysql.connector 
from model.redis_db import Redis
from datetime import timedelta 
from config import DB_CONFIG


class JournalListkModel():
    def __init__(self):
        self.conn_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "ezlife_pool",
            pool_size = 10,
            pool_reset_session = True,
            **DB_CONFIG)

    
    def get_journal_lists(self, bookId, start_dt, end_dt):
        try:
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        SELECT 
                            j.id,
                            j.date,
                            j.amount,
                            c1.name as category_main,
                            c2.name as category_object,
                            c3.name as category_character,
                            k.content,
                            s.status,
                            group_concat(
                                CONCAT('{"member_name":"', p.name, '",'),
                                CONCAT('"member_id":"', p.member_id, '",'),
                                CONCAT('"payable":"',  p.payable, '",'),
                                CONCAT('"prepaid":"',  p.prepaid, '",'),
                            '"}') as situation
                        FROM 
                            journal_list j 
                            INNER JOIN journal_list_category jc1 ON j.id = jc1.journal_list_id
                            INNER JOIN categories c1 ON jc1.categories_id = c1.id AND c1.parent_category_id = 1
                            INNER JOIN journal_list_category jc2 ON j.id = jc2.journal_list_id
                            INNER JOIN categories c2 ON jc2.categories_id = c2.id AND c2.parent_category_id = 2
                            INNER JOIN journal_list_category jc3 ON j.id = jc3.journal_list_id
                            INNER JOIN categories c3 ON jc3.categories_id = c3.id AND c3.parent_category_id = 3
                            INNER JOIN journal_list_keyword jk ON j.id = jk.journal_list_id
                            LEFT JOIN keyword k ON jk.keyword_id = k.id 
                            INNER JOIN status s ON j.id = s.journal_list_id
                            INNER JOIN (
                                SELECT p.journal_list_id, p.member_id, m.name as name, p.payable, p.prepaid
                                FROM journal_list_price p
                                INNER JOIN member m on m.id = p.member_id
                            ) p ON j.id = p.journal_list_id
                        WHERE 
                            j.book_id = %s 
                            AND j.date >= %s 
                            AND j.date < %s 
                        GROUP BY
                            j.id,
                            c1.name ,
                            c2.name ,
                            c3.name ,
                            k.content,
                            s.status
                        ORDER BY 
                            j.date DESC, 
                            j.id DESC;
                    """)
            mycursor.execute(query, (bookId, start_dt, end_dt))
            results = mycursor.fetchall()
            if results:
                    return results
            else:
                return None
            
        except mysql.connector.Error as err:
            print("Something went wrong when getting journal lists: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

            
    def create_journal_list(self,journal_list_id, date, amount, bookId, journal_list_price_value, category_main, category_object, category_character, status, created_time, keyword):
        try:    
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            mycursor.execute("START TRANSACTION")

            journal_list_value = (journal_list_id, date, amount, bookId)
            mycursor.execute("""
                INSERT INTO journal_list (id, date, amount, book_id) 
                VALUES (%s, %s, %s, %s)""", journal_list_value)

            mycursor.executemany("INSERT INTO journal_list_price (journal_list_id, member_id, prepaid, payable) VALUES (%s, %s, %s, %s)", journal_list_price_value)

            journal_list_category_value = (journal_list_id, category_main, category_object, category_character)
            mycursor.execute("""
                INSERT INTO journal_list_category (journal_list_id, categories_id) 
                SELECT %s, id FROM categories WHERE name IN (%s, %s, %s)""", journal_list_category_value)

            status_value = (journal_list_id, status, created_time)
            mycursor.execute("""
                INSERT INTO status (journal_list_id, status, created_dt) 
                VALUES (%s, %s, %s)""", status_value)  

            if keyword:
                keyword_id_in_redis = Redis.connect_to_redis().get(keyword)
                if keyword_id_in_redis:
                    journal_list_keyword_value = (journal_list_id, keyword_id_in_redis)
                    mycursor.execute("""
                    INSERT INTO journal_list_keyword (journal_list_id, keyword_id) 
                    VALUES (%s, %s)""", journal_list_keyword_value)
                else:
                    mycursor.execute("""
                        INSERT INTO keyword (content) 
                        VALUES (BINARY %s)
                        ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
                        """, (keyword,))
                    keyword_id = mycursor.lastrowid
                    journal_list_keyword_value = (journal_list_id, keyword_id)
                    mycursor.execute("""
                        INSERT INTO journal_list_keyword (journal_list_id, keyword_id) 
                        VALUES (%s, %s)""", journal_list_keyword_value)
                    Redis.connect_to_redis().set(keyword, keyword_id)
                    Redis.connect_to_redis().expire(keyword, timedelta(weeks=1))
            else:
                mycursor.execute("""
                        INSERT INTO journal_list_keyword (journal_list_id) 
                        VALUES (%s)""", (journal_list_id,))

            mycursor.execute("COMMIT")
            return "SUCCESS"

        except mysql.connector.Error as err:
            print("Something went wrong when add journal_list: {}".format(err))
            mycursor.execute("ROLLBACK")
            return "INTERNAL_SERVER_ERROR"

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()
        
    
    def delete_journal_list(self, id, status):
        try:
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            query = ("""
                        DELETE j FROM journal_list j
                        INNER JOIN status s ON j.id = s.journal_list_id
                        WHERE j.id = %s AND s.status = %s
                    """)
            mycursor.execute(query, (id, status))
            rows_affected = mycursor.rowcount
            connection_object.commit() 
            if rows_affected:
                return "SUCCESS"
            else:
                return None

        except mysql.connector.Error as err:
            print("Something went wrong when deleting journal list: {}".format(err))
            return "INTERNAL_SERVER_ERROR"
        
        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()


    def modify_journal_list(self, journal_list_id, date, amount, modified_time, bookId, journal_list_price_value, category_main, category_object, category_character, keyword):
        try:    
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            mycursor.execute("START TRANSACTION")

            journal_list_value = ( date, amount, modified_time ,bookId, journal_list_id)
            mycursor.execute("""
                UPDATE journal_list 
                SET date = %s, amount = %s, modified_dt = %s
                WHERE book_id = %s AND id = %s
            """, journal_list_value)

            mycursor.executemany("""
                UPDATE journal_list_price 
                SET prepaid = %s, payable = %s, modified_dt = %s
                WHERE journal_list_id = %s AND member_id = %s
            """, journal_list_price_value)

            journal_list_category_value = [
                    (category_main, journal_list_id, 1),
                    (category_object, journal_list_id, 2),
                    (category_character, journal_list_id, 3)]
            mycursor.executemany("""
                UPDATE journal_list_category jc
                INNER JOIN categories c ON c.id = jc.categories_id
                SET 
                    jc.categories_id = (SELECT id FROM categories WHERE name = %s)
                WHERE 
                    journal_list_id = %s
                    AND c.parent_category_id = %s
            """, journal_list_category_value)

            if keyword:
                keyword_id_in_redis = Redis.connect_to_redis().get(keyword)
                if keyword_id_in_redis:
                    journal_list_keyword_value = (keyword_id_in_redis, journal_list_id)
                    mycursor.execute("""
                        UPDATE journal_list_keyword 
                        SET keyword_id = %s
                        WHERE journal_list_id = %s
                    """, journal_list_keyword_value)
                else:
                    mycursor.execute("""
                        INSERT INTO keyword (content) 
                        VALUES (%s)
                        ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
                        """, (keyword,))
                    keyword_id = mycursor.lastrowid
                    journal_list_keyword_value = (keyword_id, journal_list_id)
                    mycursor.execute("""
                        UPDATE journal_list_keyword 
                        SET keyword_id = %s
                        WHERE journal_list_id = %s""", journal_list_keyword_value)
                    Redis.connect_to_redis().set(keyword, keyword_id)
                    Redis.connect_to_redis().expire(keyword, timedelta(weeks=1))
            else:
                 journal_list_keyword_value = (None, journal_list_id)
                 mycursor.execute("""
                        UPDATE journal_list_keyword 
                        SET keyword_id = %s
                        WHERE journal_list_id = %s""", journal_list_keyword_value)

            mycursor.execute("COMMIT")
            return "SUCCESS"
        
        except mysql.connector.Error as err:
            print("Something went wrong when edit journal_list: {}".format(err))
            mycursor.execute("ROLLBACK")
            return "INTERNAL_SERVER_ERROR"

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

    def get_status_of_journal_list(self, journal_list_id, status):
        try:
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            mycursor.execute("""
                                SELECT journal_list_id
                                FROM status
                                WHERE journal_list_id = %s AND status = %s
                            """, (journal_list_id, status))
            result = mycursor.fetchone()
            if result:
                return "已結算"
            else:
                return None    
               
        except mysql.connector.Error as err:
            print("Something went wrong when get status of journal list: {}".format(err))
            return "INTERNAL_SERVER_ERROR"

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

journalListModel = JournalListkModel()