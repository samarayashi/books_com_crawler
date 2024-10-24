import requests
from bs4 import BeautifulSoup
import json

# 設定目標URL
url = 'https://www.books.com.tw/web/sys_sublistb/books/?loc=subject_011'

# 發送請求
response = requests.get(url)
response.encoding = 'utf-8'  # 確保正確解碼
soup = BeautifulSoup(response.text, 'html.parser')

# 初始化分類結構
categories = []

# 找到所有分類區塊
for category_div in soup.find_all('div', class_='type02_s004 clearfix'):
    # 提取第一層分類名稱和連結
    main_category = category_div.find('h4').get_text(strip=True).replace('/', '_')
    main_link = category_div.find('h4').find('a')['href']

    # 初始化主分類字典
    main_category_dict = {
        'name': main_category,
        'link': main_link,
        'subcategories': []
    }

    # 提取第二層分類
    for row in category_div.find_all('tr'):
        subcategory = row.find('h5')
        if subcategory:
            subcategory_name = subcategory.get_text(strip=True).replace('/', '_')
            subcategory_link = subcategory.find('a')['href']
            subcategory_dict = {
                'name': subcategory_name,
                'link': subcategory_link,
                'subcategories': []
            }

            # 提取第三層分類
            ul_element = row.find('td').find('ul')
            if ul_element:
                # 提取所有包含<a>標籤的<li>元素
                subcategory_dict['subcategories'] = [
                    {
                        'name': li.get_text(strip=True).replace('/', '_'),
                        'link': li.find('a')['href']
                    }
                    for li in ul_element.find_all('li')
                    if li.find('a')  # 確保<li>元素中包含<a>標籤
                ]

            main_category_dict['subcategories'].append(subcategory_dict)

    categories.append(main_category_dict)

#  將結果轉換為JSON格式並寫入文件
json_output = json.dumps(categories, ensure_ascii=False, indent=4)

# 寫入文件
with open('categories.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_output)

print("JSON文件已保存為 categories.json")
