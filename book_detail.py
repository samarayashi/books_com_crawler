from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime
import json
from fake_useragent import UserAgent
import time
import random

class BookDetailScraper:
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = self._get_headers()
        self.session = requests.Session()  # 使用Session來維持Cookies
        self._setup_logging()
        self.soup = self._get_soup()

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
            filename=datetime.now().strftime('%Y%m%d') + '_book_bestseller.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _get_soup(self):
        # 隨機延遲，模擬人類行為
        time.sleep(random.uniform(1, 3))

        # 更新headers中的User-Agent
        self.headers['User-Agent'] = UserAgent().random
        response = self.session.get(self.base_url, headers=self.headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        return soup
    
    def extract_basic_info(self):
        """提取基本書籍資料"""
        try:
            info_section = self.soup.find('div', class_='type02_p003 clearfix')
            if not info_section:
                logging.error("無法找到基本資訊區塊")
                return {}

            info_list = info_section.find('ul')
            if not info_list:
                logging.error("無法找到<ul>標籤")
                return {}

            # 書名
            title = self.soup.find('h1').text.strip() if self.soup.find('h1') else "未知書名"

            # 定義要抓取的資料結構
            basic_info = {
                'title': title,
                'publisher': None,
                'publication_date': None,
                'author': None,
                'translator': None,
                'language': None,
                'price': None
            }

            # 從<ul>標籤中提取每個<li>
            for li in info_list.find_all('li'):
                if "出版社：" in li.text:
                    basic_info['publisher'] = li.find('a').text.strip() if li.find('a') else None
                elif "出版日期：" in li.text:
                    basic_info['publication_date'] = li.text.replace("出版日期：", "").strip()
                elif "作者：" in li.text:
                    basic_info['author'] = li.find('a').text.strip() if li.find('a') else None
                elif "譯者：" in li.text:
                    basic_info['translator'] = li.find('a').text.strip() if li.find('a') else None
                elif "語言：" in li.text:
                    basic_info['language'] = li.text.replace("語言：", "").strip()
            
            # 處理價格
            price_elem = info_section.find('li', class_='price')
            if price_elem:
                basic_info['price'] = price_elem.find('strong').text.strip() if price_elem.find('strong') else "未知"
            
            return basic_info

        except Exception as e:
            logging.error(f"提取基本書籍資料時出錯: {str(e)}")
            return {}

    def extract_detailed_info(self):
        """提取詳細書籍資訊"""
        try:
            details_section = self.soup.find('div', class_='mod_b type02_m058 clearfix')
            if not details_section:
                logging.error("無法找到詳細資訊區塊")
                return {}

            # 提取詳細資訊
            detail_info = {}
            detail_list = details_section.find_all('ul')[0]
            for li in detail_list.find_all('li'):
                if "ISBN：" in li.text:
                    detail_info['ISBN'] = li.text.replace("ISBN：", "").strip()
            
            # 提取書籍分類
            categories = []
            category_list = details_section.find('ul', class_='sort')
            for category in category_list.find_all('li'):
                category_path = " > ".join([link.text for link in category.find_all('a')])
                categories.append(category_path)
            
            detail_info['categories'] = categories

            return detail_info

        except Exception as e:
            logging.error(f"提取詳細書籍資料時出錯: {str(e)}")
            return {}

    def get_book_data(self):
        """獲取所有書籍資料"""
        basic_info = self.extract_basic_info()
        detailed_info = self.extract_detailed_info()
        
        # 合併所有資訊
        book_data = {**basic_info, **detailed_info}
        return book_data

def main():
    # 初始化爬取器
    scraper = BookDetailScraper(target_url)    
    # 獲取書籍資料
    book_data = scraper.get_book_data()
    
    # 輸出或保存資料
    print(json.dumps(book_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
