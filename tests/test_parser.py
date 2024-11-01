import unittest
from books_crawler.core.parser import BookInfoParser

class TestBookInfo(unittest.TestCase):

    def setUp(self):
        self.book_info = BookInfoParser()

    def test_parse_basic_info(self):
        meta_text = "書名：人類大歷史（增訂版）：從野獸到扮演上帝 【簡體版書名：人類簡史】，原文名稱：Sapiens: A Brief History of Humankind，語言：繁體中文，ISBN：9789865258900，頁數：496，出版社：天下文化，作者：哈拉瑞，譯者：林俊宏，出版日期：2022/10/27，類別：人文社科"
        self.book_info.set_meta_text(meta_text)
        result = self.book_info.parse_book_info()
        self.assertEqual(result['title'], '人類大歷史（增訂版）：從野獸到扮演上帝')
        self.assertEqual(result['simplified_title'], '人類簡史')
        self.assertEqual(result['original_title'], 'Sapiens: A Brief History of Humankind')
        self.assertEqual(result['language'], '繁體中文')
        self.assertEqual(result['isbn'], '9789865258900')
        self.assertEqual(result['pages'], '496')
        self.assertEqual(result['publisher'], '天下文化')
        self.assertEqual(result['author'], '哈拉瑞')
        self.assertEqual(result['translator'], '林俊宏')
        self.assertEqual(result['publication_date'], '2022/10/27')
        self.assertEqual(result['category'], '人文社科')

    def test_parse_with_simplified_name(self):
        meta_text = "書名：人類大歷史 【簡體版書名：人類簡史】，原文名稱：Sapiens，語言：繁體中文，ISBN：9789865258900，出版社：天下文化"
        self.book_info.set_meta_text(meta_text)
        result = self.book_info.parse_book_info()
        self.assertEqual(result['title'], '人類大歷史')
        self.assertEqual(result['simplified_title'], '人類簡史')
    
    def test_parse_with_comma_in_name(self):
        meta_text = "書名：世界上最透明的故事（日本出版界話題作，只有紙本書可以體驗的感動），原文名稱：世界でいちばん透きとおった物語，語言：繁體中文，ISBN：9789573342076，頁數：240，出版社：皇冠，作者：杉井光，譯者：簡捷，出版日期：2024/09/30，類別：文學小說"
        self.book_info.set_meta_text(meta_text)
        result = self.book_info.parse_book_info()
        self.assertEqual(result['title'], '世界上最透明的故事（日本出版界話題作，只有紙本書可以體驗的感動）')
        self.assertEqual(result['original_title'], '世界でいちばん透きとおった物語')

if __name__ == '__main__':
    unittest.main()
