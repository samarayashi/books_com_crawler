from books_crawler.core.base_scraper import BaseScraper
import yaml
import logging
from datetime import datetime


class BestsellerScraper(BaseScraper):
    def __init__(self, category, base_url, config=None):
        super().__init__(config)
        self.category = category
        self.base_url = base_url
        
    def _extract_book_id(self, url):
        """從URL中提取書籍ID"""
        try:
            if "products" in url:
                return url.split("/")[-1].split("?")[0]
            return None
        except Exception as e:
            self.logger.error(f"提取書籍ID時出錯: {str(e)}")
            return None
            
    def get_bestsellers(self):
        """爬取暢銷榜資料"""
        soup = self._get_soup(self.base_url)
        if not soup:
            return []
            
        books_data = []
        current_time = datetime.now()
        
        try:
            book_items = soup.find_all('li', class_='item')
            
            for book in book_items:
                try:
                    is_type02_bd_a = book.find('div', class_='type02_bd-a')
                    book_data = self._parse_type_a(book) if is_type02_bd_a else self._parse_type_b(book)
                    
                    if book_data:
                        book_data['timestamp'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
                        books_data.append(book_data)
                        
                except Exception as e:
                    self.logger.error(f"處理單本書籍資料時出錯: {str(e)}")
                    continue
                    
            return books_data
            
        except Exception as e:
            self.logger.error(f"爬取過程中出錯: {str(e)}")
            return []
            
    def _parse_type_a(self, book):
        """解析 A 版結構"""
        try:
            rank_elem = book.find('strong', class_='no')
            book_link = book.find('h4')
            author_elem = book.find('ul', class_='msg')
            price_elem = book.find('li', class_='price_a')
            img_elem = book.find('img', class_='cover')
            
            if not all([rank_elem, book_link, book_link.find('a')]):
                return None
                
            book_data = {
                'rank': int(rank_elem.text.strip()),
                'title': book_link.find('a').text.strip(),
                'url': book_link.find('a')['href'],
                'book_id': self._extract_book_id(book_link.find('a')['href']),
                'author': author_elem.find('a').text.strip() if author_elem and author_elem.find('a') else "未知",
                'img_url': img_elem['src'] if img_elem else None
            }
            
            if price_elem:
                book_data.update({
                    'discount': price_elem.find('b').text.strip() if price_elem.find('b') else "未知",
                    'price': price_elem.find_all('b')[-1].text.strip() if price_elem.find_all('b') else "未知"
                })
                
            return book_data
            
        except Exception as e:
            self.logger.error(f"解析A版結構時出錯: {str(e)}")
            return None
            
    def _parse_type_b(self, book):
        """解析 B 版結構"""
        try:
            rank_elem = book.find('span', class_='rank')
            book_link = book.find('h4')
            author_elem = book.find('ul')
            price_elem = book.find('p', class_='price')
            img_elem = book.find('img', class_='cover')
            
            if not all([rank_elem, book_link, book_link.find('a')]):
                return None
                
            book_data = {
                'rank': int(rank_elem.text.strip()),
                'title': book_link.find('a').text.strip(),
                'url': book_link.find('a')['href'],
                'book_id': self._extract_book_id(book_link.find('a')['href']),
                'author': author_elem.text.replace('作者：', '').strip() if author_elem else "未知",
                'img_url': img_elem['src'] if img_elem else None
            }
            
            if price_elem:
                book_data.update({
                    'discount': price_elem.find('span').text.replace('折優惠價', '').strip() if price_elem.find('span') else "未知",
                    'price': price_elem.find('b').text.strip() if price_elem.find('b') else "未知"
                })
                
            return book_data
            
        except Exception as e:
            self.logger.error(f"解析B版結構時出錯: {str(e)}")
            return None

def read_yaml_config(file_path):
    """讀取 YAML 配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"讀取配置文件時出錯: {str(e)}")
        return None

def main():
    config = read_yaml_config('books_crawler/config/book_bestseller_scraper_config.yaml')
    if not config:
        return
        
    for item in config['urls']:
        category = item['category']
        url = item['url']
        
        crawler = BestsellerScraper(category, url, config)
        bestsellers = crawler.get_bestsellers()
        
        if bestsellers:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            crawler.save_data(
                bestsellers,
                f'{category}_bestsellers_{timestamp}.json',
                format_type="json"
            )

if __name__ == "__main__":
    main() 