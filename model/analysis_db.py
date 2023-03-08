from mysql.connector import errorcode
import mysql.connector 
from config import DB_CONFIG


class AnalysisModel():
    def __init__(self):
        self.conn_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name = "ezlife_pool",
            pool_size = 10,
            pool_reset_session = True,
            **DB_CONFIG)
        

    def get_pipe(self, bookId, start_dt, end_dt):
        try:
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            query = ('''
                        SELECT sum(j.amount) as amount, c.name as category
                        FROM journal_list j
                        INNER JOIN journal_list_category jc ON j.id = jc.journal_list_id
                        INNER JOIN categories c ON jc.categories_id = c.id AND c.parent_category_id in (1, 3)
                        WHERE 
                            j.book_id = %s 
                            AND j.date >= %s 
                            AND j.date < %s  
                        GROUP BY c.name;
                    ''')
            value = (bookId, start_dt, end_dt)
            mycursor.execute(query, value)
            results = mycursor.fetchall()
            if results:
                return results

        except mysql.connector.Error as err:
            print("Something went wrong when get pipe: {}".format(err))
            return "INTERNAL_SERVER_ERROR"

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()

        
    def get_filtered_datas(self, bookId, start_dt, end_dt, category_main, category_character, category_object, keyword):
        try:
            connection_object = self.conn_pool.get_connection()
            mycursor = connection_object.cursor(dictionary=True)
            query_basic = """
                            SELECT 
                                j.id,
                                j.date, 
                                j.amount,
                                C1.name as category_main,
                                c2.name as category_object,
                                c3.name as category_character,
                                k.content as keyword,
                        """
            subquery_basic = """
                                (SELECT sum(j.amount) 
                                FROM journal_list j
                                INNER JOIN journal_list_category jc 
                                    ON j.id = jc.journal_list_id
                                INNER JOIN categories c 
                                    ON jc.categories_id = c.id AND c.parent_category_id = 1
                            """

            subquery_end = """
                                WHERE 
                                    j.book_id = %s 
                                    AND j.date >= %s 
                                    AND j.date < %s 
                                    AND c.name = C1.name 
                                GROUP BY 
                                    c.name
                                ) AS category_main_sum
                            """

            query_middle = """
                                FROM journal_list AS j
                                INNER JOIN journal_list_category jc1 
                                    ON j.id = jc1.journal_list_id
                                INNER JOIN categories C1 
                                    ON jc1.categories_id = C1.id AND C1.parent_category_id = 1
                                INNER JOIN journal_list_category jc2 
                                    ON j.id = jc2.journal_list_id
                                INNER JOIN categories c2 
                                    ON jc2.categories_id = c2.id AND c2.parent_category_id = 2
                                INNER JOIN journal_list_category jc3 
                                    ON j.id = jc3.journal_list_id
                                INNER JOIN categories c3 
                                    ON jc3.categories_id = c3.id AND c3.parent_category_id = 3
                                INNER JOIN journal_list_keyword jk 
                                    ON j.id = jk.journal_list_id
                                LEFT JOIN keyword k 
                                    ON jk.keyword_id = k.id
                                WHERE 
                                    j.book_id = %s 
                                    AND j.date >= %s 
                                    AND j.date < %s  
                            """

            query_end = """
                            Order by 
                                j.date DESC,
                                j.id DESC;
                        """

            conditions = []
            sub_conditions = []
            basic_value = (bookId, start_dt, end_dt)
            append_value = ()
            if category_main:
                conditions.append("C1.name = %s")
                sub_conditions.append("""
                    INNER JOIN journal_list_category jc1 
                    ON j.id = jc1.journal_list_id
                    INNER JOIN categories c1 
                    ON jc1.categories_id = c1.id AND c1.name = %s""")
                append_value += (category_main,)

            if category_character:
                conditions.append("c3.name = %s")
                sub_conditions.append("""
                    INNER JOIN journal_list_category jc3
                    ON j.id = jc3.journal_list_id
                    INNER JOIN categories c3 
                    ON jc3.categories_id = c3.id AND c3.name = %s""")
                append_value += (category_character,) 

            if category_object:
                conditions.append("c2.name = %s")
                sub_conditions.append("""
                    INNER JOIN journal_list_category jc2 
                    ON j.id = jc2.journal_list_id
                    INNER JOIN categories c2 
                    ON jc2.categories_id = c2.id AND c2.name = %s""")
                append_value += (category_object,) 
            
            if keyword:
                conditions.append("k.content like %s COLLATE utf8mb4_general_ci")
                sub_conditions.append("""
                    INNER JOIN journal_list_keyword jk ON j.id = jk.journal_list_id
                    RIGHT JOIN keyword k ON jk.keyword_id = k.id 
                    AND k.content like %s COLLATE utf8mb4_general_ci""")
                append_value += ("%" + keyword + "%",)

            if conditions and sub_conditions:
                query_middle += " AND " + " AND ".join(conditions)
                subquery_basic += " ".join(sub_conditions)
            
            query = (query_basic+ " " + subquery_basic + " " + subquery_end + " " + query_middle + " " + query_end)
            value = append_value + basic_value + basic_value + append_value
            mycursor.execute(query, value)
            results = mycursor.fetchall()
            if results:
                return results
            else:
                return None

        except mysql.connector.Error as err:
            print("Something went wrong when get filtered datas: {}".format(err))
            return "INTERNAL_SERVER_ERROR"

        finally:
            if connection_object.is_connected():
                mycursor.close()
                connection_object.close()



analysisModel = AnalysisModel()