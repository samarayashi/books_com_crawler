import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import List, Dict

class CategoryGenerator:
    def __init__(self):
        self.url = 'https://www.books.com.tw/web/sys_sublistb/books/?loc=subject_011'
        
    def generate_categories(self) -> List[Dict]:
        """生成分類結構"""
        response = requests.get(self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        categories = []
        for category_div in soup.find_all('div', class_='type02_s004 clearfix'):
            main_category = category_div.find('h4').get_text(strip=True).replace('/', '_')
            main_link = category_div.find('h4').find('a')['href']
            
            main_category_dict = {
                'name': main_category,
                'link': main_link,
                'subcategories': []
            }
            
            for row in category_div.find_all('tr'):
                subcategory = row.find('h5')
                if subcategory:
                    subcategory_dict = self._process_subcategory(subcategory, row)
                    main_category_dict['subcategories'].append(subcategory_dict)
                    
            categories.append(main_category_dict)
            
        return categories
        
    def _process_subcategory(self, subcategory, row) -> Dict:
        """處理子分類"""
        subcategory_name = subcategory.get_text(strip=True).replace('/', '_')
        subcategory_link = subcategory.find('a')['href']
        subcategory_dict = {
            'name': subcategory_name,
            'link': subcategory_link,
            'subcategories': []
        }
        
        ul_element = row.find('td').find('ul')
        if ul_element:
            subcategory_dict['subcategories'] = [
                {
                    'name': li.get_text(strip=True).replace('/', '_'),
                    'link': li.find('a')['href']
                }
                for li in ul_element.find_all('li')
                if li.find('a')
            ]
            
        return subcategory_dict
        
    def save_categories(self, filename: str = 'book_list_categories.json'):
        """保存分類到文件"""
        categories = self.generate_categories()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)

def main():
    generator = CategoryGenerator()
    generator.save_categories()

if __name__ == "__main__":
    main() 