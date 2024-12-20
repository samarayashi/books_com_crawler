import re

class BookInfoParser:
    patterns = {
        "title": r"書名：(.+?)(?=，(?:簡體版書名|原文名稱|語言|ISBN|出版社|作者|譯者|出版日期|類別))",
        "simplified_title": r"簡體版書名：(.+?)(?=，(?:原文名稱|語言|ISBN|出版社|作者|譯者|出版日期|類別))",
        "original_title": r"原文名稱：([^，]+)",
        "language": r"語言：([^，]+)",
        "isbn": r"ISBN：(\d+)",
        "pages": r"頁數：(\d+)",
        "publisher": r"出版社：([^，]+)",
        "author": r"作者：([^，]+)",
        "translator": r"譯者：([^，]+)",
        "publication_date": r"出版日期：([\d/]+)",
        "category": r"類別：([^，]+)"
    }

    def __init__(self, meta_text=None):
        self.meta_text = meta_text

    def set_meta_text(self, meta_text):
        self.meta_text = meta_text

    def parse_book_info(self):
        if not self.meta_text:
            return None

        result = {}

        for key, pattern in self.patterns.items():
            match = re.search(pattern, self.meta_text)
            if match:
                result[key] = match.group(1).strip()

        if "title" in result:
            simplified_title_match = re.search(r"【簡體版書名：([^】]+)】", result["title"])
            if simplified_title_match:
                result["simplified_title"] = simplified_title_match.group(1).strip()
                result["title"] = re.sub(r"【簡體版書名：[^】]+】", "", result["title"]).strip()

        return result

    @staticmethod
    def run_tests():
        test_data = [
            "書名：人類大歷史（增訂版）：從野獸到扮演上帝 【簡體版書名：人類簡史】，原文名稱：Sapiens: A Brief History of Humankind，語言：繁體中文，ISBN：9789865258900，頁數：496，出版社：天下文化，作者：哈拉瑞，譯者：林俊宏，出版日期：2022/10/27，類別：人文社科",
            "書名：世界上最透明的故事（日本出版界話題作，只有紙本書可以體驗的感動），原文名稱：世界でいちばん透きとおった物語，語言：繁體中文，ISBN：9789573342076，頁數：240，出版社：皇冠，作者：杉井光，譯者：簡捷，出版日期：2024/09/30，類別：文學小說",
            "書名：體能UP1年級生：高木直子元氣滿滿大作戰，語言：繁體中文，ISBN：9789861799049，頁數：152，出版社：大田，作者：高木直子，譯者：洪俞君，出版日期：2024/10/01，類別：生活風格"
        ]

        parser = BookInfoParser()
        for text in test_data:
            parser.set_meta_text(text)
            print(parser.parse_book_info())