import json
from airflow import DAG

from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from demojsonpath import get_word_and_examples
from demorequests import DemoRequests
from demomysql import DemoSql
import pandas as pd
from wordexception import  WordException
import pymysql
default_args = {
    'owner': 'yif_xu'
}
all_web_word = []
with DAG(
        dag_id='my_test_demo',
        default_args=default_args,
        description='test_for_work',
        schedule_interval=None,
        start_date=days_ago(1),
        tags=['test_demo']
) as dag:
    def get_word_list(**kwargs):
        ti = kwargs['ti']
        data = DemoRequests.get_liu_xue_word_list()
        w_e = WordException(len(data))

        if len(data) < 3000:
            print('单词没有完全爬取，任务出现错误！！！！')
            raise w_e
        ti.xcom_push('word_list', data)



    get_word_task = PythonOperator(
        task_id='get_word',
        python_callable=get_word_list
    )


    def get_word_detail(**kwargs):
        ti = kwargs['ti']
        word_list = ti.xcom_pull(task_ids='get_word', key='word_list')
        DemoRequests.get_all_word_detail(word_list)


    get_word_detail_task = PythonOperator(
        task_id='get_word_detail',
        python_callable=get_word_detail
    )



    def word_example_insert_to_db(**kwargs):

        json_word_detail_list = DemoSql.select_from_json_word_detail()
        demopysql = DemoSql()

        for tuple_json_list in json_word_detail_list:
            json_str = tuple_json_list[0]
            word, example_list = get_word_and_examples(json_str)
            if word == '' or example_list == []:
                continue
            for example in example_list:
                demopysql.insert_to_word_example(word, example)
        demopysql.commit()
        demopysql.close()


    word_example_insert_to_db_task = PythonOperator(
        task_id='word_example_insert_to_db_task',
        python_callable=word_example_insert_to_db
    )


    def create_csv_from_example(**kwargs):
        ti = kwargs['ti']
        conn = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456789',
            db='airflow',
            port=3306,
            charset='utf8'
        )
        df = pd.read_sql('select example from word_example ', conn)

        pd_data_source = {}
        word_list = ti.xcom_pull(task_ids='get_word', key='word_list')
        try:
            for example in df.example.tolist():
                example_word_list = example.split(' ')
                for word in example_word_list:
                    print('word = %s' % word)
                    if not word.isalpha():
                        continue
                    try:
                        word_array = pd_data_source[word]
                        word_array[0] = word_array[0] + 1
                    except Exception as e:
                        if word in word_list:
                            pd_data_source[word] = [1, True]
                        else:
                            pd_data_source[word] = [1, False]
        except Exception as e:
            print('生成错误 ， e = %s' %e)
            raise e
        else:
            df = pd.DataFrame(pd_data_source, index=['数量', '是否出现在单词爬取网站'])
            df = df.T
            df = df.sort_values(by='数量', ascending=False)
            df.to_csv('/Users/yif/Desktop/demo.csv')
        conn.close()
    create_csv_from_example_task = PythonOperator(
        task_id='create_csv_from_example_task',
        python_callable=create_csv_from_example
    )






    get_word_task >> get_word_detail_task >> word_example_insert_to_db_task  >> create_csv_from_example_task


