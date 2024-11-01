from datetime import datetime
import logging
import json
import csv
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random
import os

class BaseScraper:
    def __init__(self, config=None):
        self.config = config or {}
        self.session = requests.Session()
        self.setup_paths()
        self.setup_logging()
        self.headers = self._get_headers()
        
    def setup_paths(self):
        """設置基本路徑"""
        self.base_dir = self.config.get('base_dir', 'data')
        self.log_dir = os.path.join(self.base_dir, 'logs')
        self.output_dir = os.path.join(self.base_dir, 'output')
        
        for dir_path in [self.log_dir, self.output_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def setup_logging(self):
        """統一的日誌設置"""
        timestamp = datetime.now().strftime('%Y%m%d')
        log_filename = os.path.join(
            self.log_dir,
            f'{self.__class__.__name__.lower()}_{timestamp}.log'
        )
        
        logging.basicConfig(
            filename=log_filename,
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _get_headers(self):
        """獲取隨機User-Agent"""
        ua = UserAgent()
        return {
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.books.com.tw',
        }
        
    def _get_soup(self, url):
        """取得 BeautifulSoup 物件，包含隨機延遲模擬"""
        time.sleep(random.uniform(1, 3))
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"獲取頁面失敗: {url}, 錯誤: {str(e)}")
            return None
            
    def save_data(self, data, filename, format_type="json"):
        """統一的數據保存方法"""
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            if format_type == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif format_type == "csv":
                if not data:
                    self.logger.warning("沒有數據可以保存")
                    return
                    
                with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                    
            self.logger.info(f"數據已保存到 {output_path}")
            
        except Exception as e:
            self.logger.error(f"保存數據失敗: {str(e)}")