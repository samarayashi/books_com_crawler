from ..core.base_scraper import BaseScraper
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import pandas as pd
from typing import Dict, List, Tuple
import json

class BookListScraper(BaseScraper):
    def __init__(self, category, base_url, config=None):
        super().__init__(config)
        self.category = category
        self.base_url = base_url

    def get_category_metadata(self, soup):
        """解析頁面中的分類資訊，兼容Ａ版與Ｂ版"""
        breadcrumb = soup.find('ul', id='breadcrumb-trail')
        breadcrumb_bar = soup.find('div', class_='breadcrumb_bar')
        metadata = []
        
        if breadcrumb:
            items = breadcrumb.find_all('li')
            for item in items:
                meta_name = item.find('meta', property='name')
                if meta_name:
                    metadata.append(meta_name['content'])
                    
        if breadcrumb_bar:
            elements = breadcrumb_bar.find_all(['h3'])
            for element in elements:
                meta_name = element.find('meta', property='name')
                if meta_name:
                    metadata.append(meta_name['content'])
                    
        return metadata

    def get_total_pages(self, soup):
        """解析總頁數，兼容Ａ版與Ｂ版"""
        page_div = soup.find('div', class_='cnt_page')
        if page_div:
            page_span = page_div.find('span')
            if page_span:
                try:
                    return int(page_span.text)
                except ValueError:
                    self.logger.warning("無法解析總頁數，使用預設值 1")
                    return 1

        page_select = soup.find('div', class_='m_mod mm_031 clearfix')
        if page_select:
            try:
                total_pages = page_select.find('span').text
                return int(total_pages)
            except (ValueError, AttributeError):
                self.logger.warning("無法解析總頁數，使用預設值 1")
                return 1

        return 1

    def parse_book_info(self, item_div):
        """解析單本書的資訊"""
        book = {}
        title_link_a = item_div.find('h4').find('a')
        if title_link_a:
            book['product_name'] = title_link_a.text.strip()
            book['url'] = title_link_a['href']
        return book

    def crawl_page(self, url: str, first_page: bool = False):
        """爬取單一頁面的資訊"""
        soup = self._get_soup(url)
        if not soup:
            return [], None, None
            
        category_metadata, total_pages = None, None
        if first_page:
            category_metadata = self.get_category_metadata(soup)
            total_pages = self.get_total_pages(soup)
        
        books = []
        book_items = soup.find_all('div', class_='item')
        if not book_items:
            book_items = soup.find_all('li', class_='item')
            
        for item in book_items:
            book_info = self.parse_book_info(item)
            if book_info:
                books.append(book_info)
        
        return books, category_metadata, total_pages

    def crawl_all_pages(self, base_url: str):
        """爬取所有頁面的資訊"""
        all_books = []
        books, metadata, total_pages = self.crawl_page(base_url, first_page=True)
        all_books.extend(books)
        category_metadata = metadata

        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)

        for page in range(2, total_pages + 1):
            query_params['page'] = [str(page)]
            new_query = urlencode(query_params, doseq=True)
            page_url = urlunparse(parsed_url._replace(query=new_query))
            
            self.logger.info(f"正在爬取第 {page} 頁，共 {total_pages} 頁")
            books, _, _ = self.crawl_page(page_url)
            all_books.extend(books)
            
        return all_books, category_metadata

def main():
    categories = None
    
    try:
        with open('books_crawler/config/book_list_categories.json', 'r', encoding='utf-8') as f:
            categories = json.load(f)
    except Exception as e:
        logging.error(f"載入分類文件失敗: {str(e)}")
    
    for category in categories:
        for subcategory in category['subcategories']:
            base_url = subcategory['link']
            crawler = BookListScraper(subcategory['name'], base_url)
            all_books, category_metadata = crawler.crawl_all_pages(base_url)            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            crawler.save_data(
                all_books,
                f'{crawler.category}_category_book_list_{timestamp}.json',
                format_type="json"
            )

if __name__ == "__main__":
    main() 