from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime
import json
import csv
from fake_useragent import UserAgent
import time
import random
from re_tool.book_info import BookInfo


class BookDetailScraper:
    
    def __init__(self, log_filename=None):
        self.session = requests.Session()  # 使用Session來維持Cookies
        self.headers = self._get_headers()
        self._setup_logging(log_filename)

    def _get_headers(self):
        """獲取隨機User-Agent"""
        ua = UserAgent()
        return {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.books.com.tw',
        }

    def _setup_logging(self, log_filename=None):
        """設置日誌"""
        log_file = log_filename or datetime.now().strftime('%Y%m%d') + '_book_detail.log'
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _get_soup(self):
        """取得 BeautifulSoup 物件，包含隨機延遲模擬"""
        time.sleep(random.uniform(1, 3))  # 隨機延遲
        self.headers['User-Agent'] = UserAgent().random  # 更新 User-Agent
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
            book_info_parser = BookInfo(meta_text=content)
            book_info_dict = book_info_parser.parse_book_info()
            return book_info_dict


def save_data(data, output_format, output_path):
    """儲存資料到 JSON 或 CSV 格式"""
    if output_format == "json":
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif output_format == "csv":
        # 假設 data 為 list of dictionaries 且 keys 為統一的字段
        keys = BookInfo.patterns.keys()
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)


def main(log_filename=None, output_format="json", output_path="output.json"):
    target_urls = [
        "https://www.books.com.tw/products/0011001522?sloc=main",
        "https://www.books.com.tw/products/0010922997?sloc=ms2_6",
        # ... 其他目標 URL ...
    ]
    
    scraper = BookDetailScraper(log_filename=log_filename)
    all_books_data = []

    for url in target_urls:
        scraper.set_url(url)
        book_data = scraper.extract_basic_info()
        all_books_data.append(book_data)

    # 儲存所有資料到指定格式和位置
    save_data(all_books_data, output_format, output_path)
    print(f"資料已儲存到 {output_path}，格式：{output_format.upper()}")

if __name__ == "__main__":
    # 使用者可以自訂日誌名稱、輸出格式與路徑
    log_filename = "custom_book_detail.log"
    output_format = "csv"
    output_path = "books_data.csv"
    main(log_filename=log_filename, output_format=output_format, output_path=output_path)
