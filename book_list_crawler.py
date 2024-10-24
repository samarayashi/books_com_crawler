import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
from typing import Dict, List, Tuple
import logging
from pathlib import Path
import pandas as pd
from urllib.parse import urljoin
from fake_useragent import UserAgent
from datetime import datetime
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

class BooksCrawler:
    def __init__(self, category, base_url):
        self.category = category
        self.base_url = base_url
        self.headers = self._get_headers()
        self.session = requests.Session()  # 使用Session來維持Cookies
        self.setup_logging()

    def _get_headers(self):
        """獲取隨機User-Agent"""
        ua = UserAgent()
        return {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.books.com.tw',
        }

    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            filename = datetime.now().strftime('%Y%m%d') + '_book_list.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_category_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """解析頁面中的分類資訊"""
        breadcrumb = soup.find('ul', id='breadcrumb-trail')
        if not breadcrumb:
            return {}
        
        metadata = {}
        items = breadcrumb.find_all('li')
        for i, item in enumerate(items, 1):
            meta_name = item.find('meta', property='name')
            if meta_name:
                metadata[f'level_{i}'] = meta_name['content']
        
        return metadata

    def get_total_pages(self, soup: BeautifulSoup) -> int:
        """解析總頁數"""
        page_div = soup.find('div', class_='cnt_page')
        if not page_div:
            return 1
        
        page_span = page_div.find('span')
        if page_span:
            try:
                return int(page_span.text)
            except ValueError:
                logging.warning("無法解析總頁數，使用預設值 1")
                return 1
        return 1

    def parse_book_info(self, item_div: BeautifulSoup) -> Dict[str, str]:
        """解析單本書的資訊"""
        book = {}
        
        # 解析書名和URL
        title_link = item_div.find('h4').find('a')
        if title_link:
            book['product_name'] = title_link.text.strip()
            book['url'] = title_link['href']
            
        return book

    def crawl_page(self, url: str) -> Tuple[List[Dict[str, str]], Dict[str, str], int]:
        """爬取單一頁面的資訊"""
        time.sleep(random.uniform(1, 3))  # 隨機延遲，避免被偵測
        
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 獲取分類資訊
            category_metadata = self.get_category_metadata(soup)
            
            # 獲取總頁數
            total_pages = self.get_total_pages(soup)
            
            # 解析書籍資訊
            books = []
            book_items = soup.find_all('div', class_='item')
            for item in book_items:
                book_info = self.parse_book_info(item)
                if book_info:
                    books.append(book_info)
            
            return books, category_metadata, total_pages
            
        except Exception as e:
            logging.error(f"爬取頁面時發生錯誤: {str(e)}")
            return [], {}, 1

    def crawl_all_pages(self, base_url: str) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
        """爬取所有頁面的資訊"""
        all_books = []
        category_metadata = {}
        
        # 爬取第一頁並獲取總頁數
        books, metadata, total_pages = self.crawl_page(base_url)
        all_books.extend(books)
        category_metadata = metadata

        # 解析 base_url 以處理頁碼參數
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)

        # 爬取剩餘頁面
        for page in range(2, total_pages + 1):
            query_params['page'] = [str(page)]  # 更新頁碼參數
            new_query = urlencode(query_params, doseq=True)  # 將參數重新編碼為字串
            page_url = urlunparse(parsed_url._replace(query=new_query))  # 建立新的 URL
            
            logging.info(f"正在爬取第 {page} 頁，共 {total_pages} 頁")
            books, _, _ = self.crawl_page(page_url)
            all_books.extend(books)
            
        return all_books, category_metadata


    def save_to_json(self, data: List[Dict[str, str]], metadata: Dict[str, str], filename: str):
        """將資料保存為JSON格式"""
        output = {
            "metadata": metadata,
            "books": data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logging.info(f"資料已保存至 {filename}")

    def save_to_csv(self, data: List[Dict[str, str]], metadata: Dict[str, str], filename: str):
        """將資料保存為CSV格式"""
        # 將metadata加入每一筆書籍資料中
        for book in data:
            book.update(metadata)
            
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        logging.info(f"資料已保存至 {filename}")

    def crawl_and_save(self, url: str, output_dir: str = "output"):
        """執行爬蟲並保存資料"""
        logging.info(f"開始爬取網址: {url}")
        
        # 建立輸出目錄
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 爬取資料
        books, metadata = self.crawl_all_pages(url)
        
        # 建立檔名
        category_name = "_".join(metadata.values())
        base_filename = f"{category_name}_{time.strftime('%Y%m%d_%H%M%S')}"
        
        # 保存資料
        self.save_to_json(books, metadata, f"{output_dir}/{base_filename}.json")
        self.save_to_csv(books, metadata, f"{output_dir}/{base_filename}.csv")
        
        logging.info("爬蟲完成")

def main():
    with open('categories_test.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)

    # 逐一爬取每個第二層子類別
    for category in categories:
        for subcategory in category['subcategories']:
            base_url = subcategory['link']
            crawler = BooksCrawler(subcategory['name'], base_url)
            crawler.crawl_and_save(base_url)

if __name__ == "__main__":
    main()