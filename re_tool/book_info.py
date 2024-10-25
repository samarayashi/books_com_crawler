# book_info.py
import re

class BookInfo:
    def __init__(self, meta_text=None):
        """
        初始化 BookInfo 類別，並可選擇傳入 meta_text 進行分析。
        """
        self.meta_text = meta_text
        self.patterns = {
            "書名": r"書名：(.+?)(?=，(?:簡體版書名|原文名稱|語言|ISBN|出版社|作者|譯者|出版日期|類別))",
            "簡體版書名": r"簡體版書名：(.+?)(?=，(?:原文名稱|語言|ISBN|出版社|作者|譯者|出版日期|類別))",
            "原文名稱": r"原文名稱：([^，]+)",
            "語言": r"語言：([^，]+)",
            "ISBN": r"ISBN：(\d+)",
            "頁數": r"頁數：(\d+)",
            "出版社": r"出版社：([^，]+)",
            "作者": r"作者：([^，]+)",
            "譯者": r"譯者：([^，]+)",
            "出版日期": r"出版日期：([\d/]+)",
            "類別": r"類別：([^，]+)"
        }

    def set_meta_text(self, meta_text):
        """
        設定新的 meta_text，允許重複使用同一個 BookInfo 物件進行不同的資料解析。
        """
        self.meta_text = meta_text

    def parse_book_info(self):
        """
        從 meta_text 解析書籍資訊，並返回字典。
        """
        if not self.meta_text:
            return None

        result = {}

        # 逐一匹配模式並提取資訊
        for key, pattern in self.patterns.items():
            match = re.search(pattern, self.meta_text)
            if match:
                result[key] = match.group(1).strip()

        # 處理特殊情況 - 書名中的簡體版書名
        if "書名" in result:
            simplified_title_match = re.search(r"【簡體版書名：([^】]+)】", result["書名"])
            if simplified_title_match:
                result["簡體版書名"] = simplified_title_match.group(1).strip()
                # 將書名中的簡體版書名部分移除
                result["書名"] = re.sub(r"【簡體版書名：[^】]+】", "", result["書名"]).strip()

        return result

    @staticmethod
    def run_tests():
        """
        執行內建測試案例，檢查解析功能是否正常運作。
        """
        test_data = [
            "書名：人類大歷史（增訂版）：從野獸到扮演上帝 【簡體版書名：人類簡史】，原文名稱：Sapiens: A Brief History of Humankind，語言：繁體中文，ISBN：9789865258900，頁數：496，出版社：天下文化，作者：哈拉瑞，譯者：林俊宏，出版日期：2022/10/27，類別：人文社科",
            "書名：世界上最透明的故事（日本出版界話題作，只有紙本書可以體驗的感動），原文名稱：世界でいちばん透きとおった物語，語言：繁體中文，ISBN：9789573342076，頁數：240，出版社：皇冠，作者：杉井光，譯者：簡捷，出版日期：2024/09/30，類別：文學小說",
            "書名：體能UP1年級生：高木直子元氣滿滿大作戰，語言：繁體中文，ISBN：9789861799049，頁數：152，出版社：大田，作者：高木直子，譯者：洪俞君，出版日期：2024/10/01，類別：生活風格"
        ]

        book_info = BookInfo()
        for text in test_data:
            book_info.set_meta_text(text)
            print(book_info.parse_book_info())
