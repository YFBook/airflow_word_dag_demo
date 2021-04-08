## Demo实现

1. 爬取3000单词网的单词，然后访问word api 接口，存储其返回的json数据到mysql
2. 从mysql 中 获取**步骤1** 得到的数据记录，提取单词和例句，存入另外一张mysql表（B表）中
3.  使用pandas提取B表数据中的例句，提取例句中出现的**所有单词**，输出一份单词出现次数的**从大到小**的排序的csv文件，需要包含三列:
   * 单词
   * 出现次数
   * 该单词是否出现在3000单词网中



## Demo要求

要求：给到一种方式证明整个任务确实全部正常执行完了，没有漏爬取，漏统计的单词。

方案： 已知单词数目3000，在task中设置爬取到的单词数量小于3000时抛出错误；在dag执行时，通过web UI观看其运行状态（树状图等），即可清晰了解任务是否执行完毕，是否存在漏爬取单词。



## 实现步骤

1. 安装airflow

2. 安装代码使用到的库： lxml、jsonpath、requests、pandas、pymysql

3. 安装mysql，安装完成后，创建数据库:`` create database airflow;``

4. airflow.cfg关于mysql配置：

   `sql_alchemy_conn = mysql+pymysql://airflow:airflow@localhost:3306/airflow`

5. 创建mysql用户：``create user 'airflow'@'localhost' identified by 'airflow';`

6. 用户授权：

   ```
   grant all on airflow.* to 'airflow'@'%';
   flush privileges;
   ```

7. 初始化airflow: ``airflow db init``

8. 进入AIRFLOW_HOME的路径目录（默认是~/airflow），然后将demo中的dags文件夹移入

9. 启动服务和调度器: 

   ``` 
   airflow webserver --port 8080
   airflow scheduler 
   ```

10. 创建airflow用户: 

    ```
    airflow users create -u admin -f word -l demo -r admin -e emaile@qq.com
    ```

11. 用浏览器打开本地服务：http://localhost:8080/  ,登录后进入主页， 即可看到自定义的dags：my_test_demo

12. 创建两个题目要求的表用于存放数据，创表语句:

    * ```
      +--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
      | Table        | Create Table                                                                                                                                                                                                                  |
      +--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
      | word_example | CREATE TABLE `word_example` (
        `id` int unsigned NOT NULL AUTO_INCREMENT,
        `word` varchar(255) NOT NULL,
        `example` varchar(255) NOT NULL,
        PRIMARY KEY (`id`)
      ) ENGINE=InnoDB AUTO_INCREMENT=38554 DEFAULT CHARSET=utf8 |
      +--------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
      ```

    * ```
      +------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
      | Table            | Create Table                                                                                                                                                                              |
      +------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
      | json_word_detail | CREATE TABLE `json_word_detail` (
        `id` int unsigned NOT NULL AUTO_INCREMENT,
        `data` json DEFAULT NULL,
        PRIMARY KEY (`id`)
      ) ENGINE=InnoDB AUTO_INCREMENT=11816 DEFAULT CHARSET=utf8 |
      +------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
      
      ```

13. 修改**word_demo.py** 内第111行代码， 将 `df.to_csv('/Users/yif/Desktop/demo.csv')`  其路径修改成本地桌面路径：```df.to_csv('本地路径')``   （确认有权限写入的路径）

14. 修改**word_demo.py** 内的函数```create_csv_from_example``代码中关于数据库的配置

15. 修改**demomysql.py**内函数·```__init__``` 关于数据库的配置

16. 在web ui上手动触发 该自定义的dag

17. 等待dag执行完成后，即可在上面修改的路径中查阅生成的csv文件或可查看已跑通后生成的```demo.csv``` 

## 运行时可能出现的问题

1.task自动结束，log输出：```INFO - Task exited with return code Negsignal.SIGABRT```

解决方法：  防止task过早结束，通过修改 修改airflow.cfg配置 ->killed_task_cleanup_time = 604800



## 安装airflow问题

太多，此处不进行描述，都可通过google解决





