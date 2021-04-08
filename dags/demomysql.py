import pymysql
import threading


class DemoSql:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='airflow',
                                    charset='utf8')
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()


    @classmethod
    def insert_all_word_detail(cls, word_detail_list):
        sql = DemoSql()
        print('插入长度 = %s' % len(word_detail_list))
        for jsonStr in word_detail_list:
            insert_thread = threading.Thread(target=sql.insert_to_json_word_detail, args=(jsonStr,))
            insert_thread.setDaemon(True)
            insert_thread.start()
            insert_thread.join()
        sql.close()
    @classmethod
    def select_from_json_word_detail(cls):
        sql = DemoSql()
        ex_sql = 'select data from json_word_detail';
        result = ()
        try:
            sql.cursor.execute(ex_sql)
            result = sql.cursor.fetchall()
        except Exception as e:
            print('select failure')
        finally:
            sql.close()
        return  result
    def insert_to_json_word_detail(self, jsonStr):

        try:
            sql = "insert into json_word_detail values (null,%s)"
            print("sql = %s" % sql)
            print(' word = %s' %jsonStr)
            self.cursor.execute(sql, [jsonStr])

        except Exception as e:
            self.conn.rollback()
            print(e)
    def commit(self):
        self.conn.commit()
    def insert_to_word_example(self,word, example):
        try:
            sql = "insert into word_example values (null,%s,%s)"
            self.cursor.execute(sql, [word, example])
        except Exception as e:
            self.conn.rollback()
            print(e)
    def get_count(self):
        sql = 'select count(*) from word_example'
        result = ()
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
        except Exception as e:
            print('数量获取失败 = %s' % e)
        return result
    def get_all_example(self):
        sql = 'select example from word_example'
        result = ()
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            print('获取例句失败 = %s' % e)
        return  result
    def get_example(self, pageindex, pagesize):
        sql = 'select example from word_example limit %s,%s'
        print('开始查询，下标: %s' %pageindex)
        result = ()
        try:
            self.cursor.execute(sql, [pageindex, pagesize])
            result = self.cursor.fetchall()
        except Exception as e:
            print('获取例句失败 = %s' % e)
        return result

