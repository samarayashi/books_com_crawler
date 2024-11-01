from ..core.base_scraper import BaseScraper
from ..core.parser import BookInfoParser
from datetime import datetime

class BookDetailScraper(BaseScraper):
    def __init__(self, config=None):
        super().__init__(config)
        self.url = None
        self.soup = None
        
    def set_url(self, url):
        """設定新的目標 URL 並取得解析的 BeautifulSoup 物件"""
        self.url = url
        self.soup = self._get_soup(url)
        
    def extract_basic_info(self):
        """提取基本書籍資料"""
        if not self.soup:
            self.logger.error("沒有可用的網頁內容")
            return None
            
        try:
            meta_description = self.soup.find('meta', attrs={'name': 'description'})
            if meta_description:
                content = meta_description.get('content')
                book_info_parser = BookInfoParser(meta_text=content)
                return book_info_parser.parse_book_info()
        except Exception as e:
            self.logger.error(f"提取書籍資訊失敗: {str(e)}")
            return None
        
    def extract_category_detail(self):
        '''提取書籍詳細類別資料'''
        if not self.soup:
            self.logger.error("沒有可用的網頁內容")
            return None

        try:
            categories = {'detail_category': []}  # 使用 'detail_category' 作為鍵
            category_list = self.soup.find('ul', class_='sort')
            
            if category_list:
                for li in category_list.find_all('li'):
                    # 移除 "本書分類：" 文字
                    li_text = li.get_text(strip=True).replace('本書分類：', '')
                    
                    # 分割類別路徑
                    categories = li_text.split('>')
                    
                    # 清理每個類別名稱
                    categories = [
                        name.strip().replace('/', '_')
                        for name in categories
                    ]
                    
                    # 將每個分類名稱列表加入 categories 字典
                    categories['detail_category'].append(categories)

            return categories
        except Exception as e:
            print("提取書籍類別資料失敗")
            self.logger.error(f"提取書籍類別資料失敗: {str(e)}")
            return None

    

def main(config=None):
    target_urls = [
        "https://www.books.com.tw/products/0011001522?sloc=main",
        "https://www.books.com.tw/products/0010922997?sloc=ms2_6",
        "https://www.books.com.tw/products/E050238022?loc=P_0004_002",
        "https://www.books.com.tw/products/0011004550?loc=P_0003_001",
        "https://www.books.com.tw/products/0011004419?loc=P_0003_001"
    ]
    
    all_books_data = []
    for url in target_urls:
        scraper = BookDetailScraper(config)
        scraper.set_url(url)
        book_info_data = scraper.extract_basic_info()
        book_category_data = scraper.extract_category_detail()
        if book_info_data:
            all_books_data.append({**book_info_data, **book_category_data})
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    scraper.save_data(
        all_books_data,
        f'book_details_{timestamp}.json',
        format_type="json"
    )

if __name__ == "__main__":
    main() 