import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
import logging
from fake_useragent import UserAgent
import json
import ymal


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
            filename='crawler.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _extract_book_id(self, url):
        """從URL中提取書籍ID"""
        try:
            if "products" in url:
                book_id = url.split("/")[-1].split("?")[0]
                return book_id
            return None
        except Exception as e:
            logging.error(f"提取書籍ID時出錯: {str(e)}")
            return None

    def _extract_price(self, price_text):
        """從價格文字中提取數字"""
        print(price_text)
        try:
            # 移除所有空白字符
            price_text = ''.join(price_text.split())
            
            if '折' in price_text:
                # 處理折扣+價格格式: 77折400元
                discount_part, price_part = price_text.split('折')
                price = price_part.replace('元', '').strip()
                discount = discount_part
            else:
                # 處理純價格格式: 599元
                price = price_text.replace('元', '').strip()
                discount = 100  # 無折扣時設為100
                
            # 提取折扣和價格
            return int(discount), int(price)
        except Exception as e:
            logging.error(f"提取價格時出錯: {str(e)}")
            return None, None

    def get_bestsellers(self):
        """爬取暢銷榜資料"""
        try:
            # 隨機延遲，模擬人類行為
            time.sleep(random.uniform(1, 3))

            # 更新headers中的User-Agent
            self.headers['User-Agent'] = UserAgent().random

            response = self.session.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            books_data = []
            current_time = datetime.now()

            # 獲取所有li class為'item'的元素
            book_items = soup.find_all('li', class_='item')
            
            for book in book_items:
                try:
                    # 檢查是否是 A 版結構
                    is_type02_bd_a = book.find('div', class_='type02_bd-a')
                    if is_type02_bd_a:
                        # A 版解析邏輯
                        rank_elem = book.find('strong', class_='no')
                        book_link = book.find('h4')
                        author_elem = book.find('ul', class_='msg')
                        price_elem = book.find('li', class_='price_a')
                        img_elem = book.find('img', class_='cover')
                    else:
                        # B 版解析邏輯
                        rank_elem = book.find('span', class_='rank')
                        book_link = book.find('h4')
                        author_elem = book.find('ul')
                        price_elem = book.find('p', class_='price')
                        img_elem = book.find('img', class_='cover')
                    
                    # 基本資料驗證
                    if not rank_elem or not book_link or not book_link.find('a'):
                        continue
                    
                    # 獲取排名
                    rank = rank_elem.text.strip()
                    
                    # 獲取書籍連結和標題
                    title = book_link.find('a').text.strip()
                    url = book_link.find('a')['href']
                    
                    # 獲取作者
                    if author_elem and author_elem.find('a'):
                        author = author_elem.find('a').text.strip()
                    else:
                        # 如果 A 版的 'a' 元素不存在，則嘗試直接查找 'li' 中的文本 (B 版)
                        author = author_elem.text.strip() if author_elem else "未知"
                    
                    # 獲取價格資訊
                    if price_elem:
                        price_text = price_elem.text.replace('優惠價：', '').replace('折優惠價', '').strip()
                        discount, price = self._extract_price(price_text)
                    else:
                        discount, price = None, None
                    
                    # 提取書籍ID
                    book_id = self._extract_book_id(url)
                    
                    # 獲取圖片URL
                    img_url = img_elem['src'] if img_elem else None

                    # 只有當所有必要資料都存在時才添加到結果中
                    if all([rank, title, url, book_id]):
                        books_data.append({
                            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'rank': int(rank),
                            'title': title,
                            'author': author,
                            'book_id': book_id,
                            'url': url,
                            'discount': discount,
                            'price': price,
                            'img_url': img_url
                        })

                except Exception as e:
                    logging.error(f"處理單本書籍資料時出錯: {str(e)}")
                    logging.debug(f"問題數據: {book}")
                    continue

            return books_data

        except requests.RequestException as e:
            logging.error(f"請求網頁時出錯: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"爬取過程中出錯: {str(e)}")
            return []

    def save_to_csv(self, data, filename=None):
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f'{self.category}_bestsellers_{timestamp}.csv'
        # 其他內容保持不變

    def save_to_json(self, data, filename=None):
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f'{self.category}_bestsellers_{timestamp}.json'
            """將數據保存為JSON文件"""
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                filename = f'bestsellers_{timestamp}.json'
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logging.info(f"數據已保存到 {filename}")
                return True
            except Exception as e:
                logging.error(f"保存JSON文件時出錯: {str(e)}")
                return False


def read_yaml_config(filename):
    """讀取 YAML 配置文件"""
    with open(filename, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def scrape_category(category, url):
    """執行抓取任務"""
    crawler = BooksCrawler(category, url)
    logging.info(f"開始爬取 {category}...")
    bestsellers = crawler.get_bestsellers()
    if bestsellers:
        crawler.save_to_csv(bestsellers)
        crawler.save_to_json(bestsellers)
        logging.info(f"成功爬取 {len(bestsellers)} 筆數據來自 {category}")
    else:
        logging.error(f"{category} 未能獲取任何數據")

def main():
    # 讀取 YAML 文件
    config = read_yaml_config('config.yaml')  # 假設你的 YAML 文件名為 config.yaml
    
    for item in config['urls']:
        category = item['category']
        url = item['url']
        frequency = item.get('frequency', 'hourly')  # 預設為 'hourly'
        
        # 暫時未處理排程頻率部分
        # 在這裡可以根據 frequency 設置 schedule，例如：
        # if frequency == "hourly":
        #     schedule.every().hour.at(":00").do(scrape_category, category, url)
        # elif frequency == "daily":
        #     schedule.every().day.at("02:00").do(scrape_category, category, url)
        
        # 現在手動運行每一個 URL
        scrape_category(category, url)
    
    # 掛載持續運行排程: 感覺可以用lambda或是其他saas排程，如果我沒有用持續開著容器或伺服器的話
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

if __name__ == "__main__":
    main()
