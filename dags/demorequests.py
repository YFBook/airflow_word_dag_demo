import requests
from lxml import etree
import threading
from demomysql import DemoSql
import copy
liuxue_url = 'https://liuxue.ef.com.cn/english-references/english-vocabulary/top-3000-words/'
liuxue_cookie = '__cfduid=d85804872a39da83653942c32cec060c41617072252; mc=CN; efcc=CN; efdomain=liuxue.ef.com.cn; TrackingData=SourceCode:00700|PartnerName:internet general|Etag:not set|Keyword:|RawSourceEtag:undefined; dmpgEtag=JTIyMDA3MDAlMkNub3QlMjBzZXQlMjI=; LatestTrackingData=SourceCode:00700|PartnerName:internet general|Etag:not set|Keyword:|RawSourceEtag:undefined; OriginalReferringURl=; gaPropId=UA-151204776-49; _gcl_au=1.1.1422267237.1617072252; _ga=GA1.3.550486068.1617072252; _scid=61584584-9d96-4403-89a5-4aa0f42a47ae; _fbp=fb.2.1617072253442.1085688015; _sctr=1|1617033600000; _gid=GA1.3.1358640582.1617762885; efDTMVisit=JTdCJTIydmlzaXQlMjIlM0ElN0IlMjJzdGFydCUyMiUzQSU3QiUyMnRpbWUlMjIlM0ElMjIlRTQlQjglOEElRTUlOEQlODgxMSUzQTI4JTNBMjMlMjIlMkMlMjJ0aW1lc3RhbXAlMjIlM0ExNjE3NzY2MTAzNzg0JTJDJTIyZGF0ZSUyMiUzQSUyMjctMy0yMDIxJTIyJTdEJTJDJTIyY3VycmVudCUyMiUzQSU3QiUyMnRpbWUlMjIlM0ElMjIlRTQlQjglOEElRTUlOEQlODgxMSUzQTI4JTNBMjMlMjIlMkMlMjJ0aW1lc3RhbXAlMjIlM0ExNjE3NzY2MTAzNzg0JTJDJTIyZGF0ZSUyMiUzQSUyMjctMy0yMDIxJTIyJTdEJTJDJTIycHJldmlvdXMlMjIlM0ElN0IlMjJ0aW1lJTIyJTNBJTIyJUU0JUI4JThBJUU1JThEJTg4MTAlM0EzNCUzQTQ0JTIyJTJDJTIydGltZXN0YW1wJTIyJTNBMTYxNzc2Mjg4NDk2NSUyQyUyMmRhdGUlMjIlM0ElMjI3LTMtMjAyMSUyMiU3RCU3RCUyQyUyMmN1c3RvbWVyJTIyJTNBJTdCJTIydHlwZSUyMiUzQSUyMnJlcGVhdCUyMiUyQyUyMnZhbHVlJTIyJTNBMSUyQyUyMm51bU9mUGFnZXMlMjIlM0ExJTdEJTdE; OriginalEntryUrl=https://liuxue.ef.com.cn/english-references/english-vocabulary/top-3000-words/; _gat_UA-151204776-49=1; triton=656400814; tts=id=777698237&t=356247905; pageview=1510535101'
api_url = 'https://www.wordsapi.com/mashape/words/'
api_url_params = '?when=2021-04-05T06:47:48.314Z&encrypted=8cfdb18be722979bea9407bfe958babeaeb4250933fe93b8'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'


class DemoRequests:
    need_to_request_against_word=[]
    def __init__(self, url):
        print('初始化-----')
        self.url = url

    def get_res(self):
        requests.adapters.DEFAULT_RETRIES = 30
        s = requests.session()
        s.keep_alive = False
        return s.get(self.url, headers=self.headers, verify=False, timeout = 3)

    @classmethod
    def get_liu_xue_word_list(cls):
        req = DemoRequests(liuxue_url)
        req.headers = {
            "User-Agent": user_agent,
            "Cookie": liuxue_cookie
        }
        return req.get_liu_xue_word_data()

    @classmethod
    def get_word_detail(cls, word,sql):
        word_url = api_url + word + api_url_params
        req = DemoRequests(word_url)
        req.headers = {
            "User-Agent": user_agent,
        }
        try:
            response = req.get_res()
            sql.insert_to_json_word_detail(response.text)
        except Exception as e :
            print('单词详情错误，e = %s' %e)
            DemoRequests.need_to_request_against_word.append(word)
        return response.text

    @classmethod
    def get_all_word_detail(cls, word_list):
        print('开始获取单词详情')
        demomysql = DemoSql()

        for word in word_list:
            print('--------word = %s' % word)
            word_thread = threading.Thread(target=DemoRequests.get_word_detail, args=(word,demomysql))
            word_thread.setDaemon(True)
            word_thread.start()
            word_thread.join()
        if len(DemoRequests.need_to_request_against_word) > 0:
            print('继续查找，需要查找单词数目 = %s' %len(DemoRequests.need_to_request_against_word))
            need_to_request_against_word = copy.deepcopy(DemoRequests.need_to_request_against_word)
            DemoRequests.need_to_request_against_word = []
            DemoRequests.get_all_word_detail(need_to_request_against_word)
        demomysql.commit()
        print('获取完毕')

    def get_liu_xue_word_data(self):
        print('获取数据 , url = %s' % self.url)
        response = self.get_res()
        words = self.parse_html_data(response.content)
        print('单词数 = %s' %len(words))
        return words

    def parse_html_data(self, data):
        print('解析数据')
        html = data.decode()
        html = etree.HTML(html)
        p_html = html.xpath("//div[@class='field-item even']/p")
        p_html = p_html[1]
        words_list = p_html.xpath('./text()')
        for i in range(len(words_list)):
            words_list[i] = words_list[i].strip()
        return words_list


if __name__ == '__main__':
    data = DemoRequests.get_liu_xue_word_list()
    print(data)
