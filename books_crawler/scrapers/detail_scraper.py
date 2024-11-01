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

def main(config=None):
    target_urls = [
        "https://www.books.com.tw/products/0011001522?sloc=main",
        "https://www.books.com.tw/products/0010922997?sloc=ms2_6",
    ]
    
    scraper = BookDetailScraper(config)
    all_books_data = []
    
    for url in target_urls:
        scraper.set_url(url)
        book_data = scraper.extract_basic_info()
        if book_data:
            all_books_data.append(book_data)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    scraper.save_data(
        all_books_data,
        f'book_details_{timestamp}.json',
        format_type="json"
    )

if __name__ == "__main__":
    main() 