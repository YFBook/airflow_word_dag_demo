class WordException(Exception):
    def __init__(self, word_len):
        self.word_len = word_len

    def __str__(self):
        return '长度为 = {%s}, 爬取错误！', self.word_len