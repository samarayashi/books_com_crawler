import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time
import random
from fake_useragent import UserAgent
import json
import re

class BooksCrawler:
    def __init__(self, base_url):
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
            'Referer': 'https://www.chimingpublishing.com',
        }

    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            filename=datetime.now().strftime('%Y%m%d') + '_book_bestseller.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _extract_ranking_data(self, soup):
        """從解析後的soup中提取排行榜數據"""
        try:
            ranking_data = []
            # 尋找包含 'series' 的 <script> 標籤
            script_tag = soup.find('script', string=lambda text: text and 'series' in text)

            if not script_tag:
                logging.error("未找到包含排行榜數據的script標籤")
                return ranking_data
            
            # 解析script內容，提取排行榜數據
            start_index = script_tag.string.index('series:') + len('series: ')  # 找到series開始的索引
            end_index = script_tag.string.rindex(']') + 1  # 找到series結束的索引
            # 拿到js中map轉成的字串
            series_data = script_tag.string[start_index:end_index]
            
            # 轉換為有效的 JSON 格式
            def replace_date_utc(match):
                # 擷取 UTC 參數
                params = match.group(1).split(', ')
                year = int(params[0])  # 年份
                month = int(params[1])  # 月份
                day = int(params[2])  # 日
                return f'"{year}-{month + 1:02d}-{day:02d}"'  # 轉為字符串格式

            # 使用正則表達式替換
            series_data = re.sub(r'Date\.UTC\((.*?)\)', replace_date_utc, series_data)

            # 將鍵名用雙引號包起來
            series_data = re.sub(r'(\w+):', r'"\1":', series_data)
            series_list = json.loads(series_data)

            for series in series_list:
                rank_info = {
                    'name': series['name'],
                    'data': series['data']
                }
                ranking_data.append(rank_info)

            return ranking_data
        except Exception as e:
            logging.error(f"提取排行榜數據時出錯: {str(e)}")
            return []

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

            ranking_data = self._extract_ranking_data(soup)

            # 日誌記錄爬取結果
            logging.info(f"成功提取{len(ranking_data)}條排行榜數據")
            return ranking_data

        except requests.RequestException as e:
            logging.error(f"請求網頁時出錯: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"爬取過程中出錯: {str(e)}")
            return []

if __name__ == "__main__":
    base_url = "https://www.chimingpublishing.com/monster/book/0011001520"
    crawler = BooksCrawler(base_url)
    bestsellers = crawler.get_bestsellers()
    print(json.dumps(bestsellers, indent=4, ensure_ascii=False))
