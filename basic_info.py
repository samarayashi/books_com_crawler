from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime
import json
from fake_useragent import UserAgent
import time
import random
from re_tool import book_info


class BookDetailScraper:
    
    def __init__(self):
        self.session = requests.Session()  # 使用Session來維持Cookies
        self.headers = self._get_headers()
        self._setup_logging()

    def _get_headers(self):
        """獲取隨機User-Agent"""
        ua = UserAgent()
        return {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.books.com.tw',
        }

    def _setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            filename=datetime.now().strftime('%Y%m%d') + '_book_detail.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _get_soup(self):
        # 隨機延遲，模擬人類行為
        time.sleep(random.uniform(1, 3))

        # 更新headers中的User-Agent
        self.headers['User-Agent'] = UserAgent().random
        response = self.session.get(self.url, headers=self.headers, timeout=10)
        response.raise_for_status()

        return BeautifulSoup(response.text, 'html.parser')
    
        
    def set_url(self, url):
        """設定新的目標 URL 並取得解析的 BeautifulSoup 物件"""
        self.url = url
        self.soup = self._get_soup()

    def extract_basic_info(self):
        """提取基本書籍資料"""
        meta_description = self.soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            content = meta_description.get('content')
            book_info_parser = book_info.BookInfo(meta_text=content)
            book_info_dict = book_info_parser.parse_book_info()
            return book_info_dict


def main():
    target_urls = [
        "https://www.books.com.tw/products/0011001522?sloc=main",
        "https://www.books.com.tw/products/0010922997?sloc=ms2_6",
        # ... 其他目標 URL ...
    ]
    
    scraper = BookDetailScraper()
    all_books_data = []

    for url in target_urls:
        scraper.set_url(url)
        book_data = scraper.extract_basic_info()
        all_books_data.append(book_data)
    
    # 輸出或保存所有資料
    print(json.dumps(all_books_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
