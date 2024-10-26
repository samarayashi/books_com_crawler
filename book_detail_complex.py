from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime
import json
from fake_useragent import UserAgent
import time
import random

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
        try:
            # 書名
            book_name = self.soup.select_one('div.grid_10 h1').text.strip()
            
            # 原文書名:此區塊有可能為空
            ori_book_name = self.soup.select_one('div.grid_10 h2')
            ori_book_name = ori_book_name.text.strip() if ori_book_name else None

            # 在type02_p003區塊中尋找基本資訊
            info_div = self.soup.select_one('div.type02_p003')
            
            # 初始化資料字典
            basic_info = {
                'book_name': book_name,
                'ori_book_name': ori_book_name,
                'author': None,
                'ori_author': None,
                'translator': None,
                'publisher': None,
                'publish_date': None,
                'language': None
            }
            
            # 遍歷所有li元素
            for li in info_div.select('li'):
                text = li.get_text(strip=True)
                
                if '作者' in text:
                    # 修改作者提取邏輯：尋找包含 search/query/key/ 的連結
                    author_link = li.select_one('a[href*="search/query/key/"]')
                    if author_link:
                        basic_info['author'] = author_link.text.strip()
                elif '作者原文' in text:
                    ori_author_link = li.select_one('a[href*="search/query/key/"]')
                    if ori_author_link:
                        basic_info['ori_author'] = author_link.text.strip()
                elif '譯者' in text:
                    translator_link = li.select_one('a[href*="search/query/key/"]')
                    if translator_link:
                        basic_info['translator'] = translator_link.text.strip()
                elif '出版社' in text:
                    basic_info['publisher'] = li.select_one('a span').text.strip()
                elif '出版日期' in text:
                    basic_info['publish_date'] = text.split('：')[1].strip()
                elif '語言' in text:
                    basic_info['language'] = text.split('：')[1].strip()
                    
            logging.info(f"Successfully extracted basic info for book: {book_name}")
            return basic_info
            
        except Exception as e:
            logging.error(f"Error extracting basic info: {str(e)}")
            return {}

    def extract_detailed_info(self):
        """提取詳細書籍資訊"""
        try:
            # 找到詳細資料區塊
            detail_div = self.soup.select_one('div.mod_b.type02_m058')
            
            categories = []
            if detail_div:
                # 尋找所有分類資訊
                for li in detail_div.select('ul.sort li'):
                    if '本書分類' in li.text:
                        # 獲取所有分類連結的文字並用 > 連接
                        category = ' > '.join([a.text.strip() for a in li.select('a')])
                        categories.append(category)
            
            detailed_info = {
                'categories': categories
            }
            
            logging.info("Successfully extracted detailed info")
            return detailed_info
            
        except Exception as e:
            logging.error(f"Error extracting detailed info: {str(e)}")
            return {}

    def extract_price_info(self):
        """提取價格相關資訊"""
        try:
            price_div = self.soup.select_one('div.cnt_prod002 div.prod_cont_b')
            
            price_info = {
                'list_price': '',
                'sale_price': '',
                'discount': '',
                'discount_deadline': ''
            }
            
            if price_div:
                price_items = price_div.select('ul.price li')
                for item in price_items:
                    text = item.get_text(strip=True)
                    
                    if '定價' in text:
                        price_info['list_price'] = item.select_one('em').text.strip()
                    elif '優惠價' in text:
                        # 取得折扣率
                        discount = item.select_one('strong b').text.strip()
                        price_info['discount'] = f"{discount}折"
                        
                        # 取得優惠價格
                        sale_price = item.select_one('strong.price01 b').text.strip()
                        price_info['sale_price'] = sale_price
                    elif '優惠期限' in text:
                        price_info['discount_deadline'] = text.split('：')[1]
            
            logging.info("Successfully extracted price info")
            return price_info
            
        except Exception as e:
            logging.error(f"Error extracting price info: {str(e)}")
            return {}
        
    def get_book_data(self):
        """獲取所有書籍資料"""
        basic_info = self.extract_basic_info()
        detailed_info = self.extract_detailed_info()
        price_info = self.extract_price_info()
        # 合併所有資訊
        return {**basic_info, **detailed_info, **price_info}

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
        book_data = scraper.get_book_data()
        all_books_data.append(book_data)
    
    # 輸出或保存所有資料
    print(json.dumps(all_books_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
