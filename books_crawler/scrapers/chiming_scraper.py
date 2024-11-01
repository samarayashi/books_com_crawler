from ..core.base_scraper import BaseScraper
import json
import re
from datetime import datetime

class ChimingBestsellerScraper(BaseScraper):
    def __init__(self, base_url, config=None):
        super().__init__(config)
        self.base_url = base_url
        self.headers['Referer'] = 'https://www.chimingpublishing.com'

    def _extract_ranking_data(self, soup):
        """從解析後的soup中提取排行榜數據"""
        try:
            ranking_data = []
            script_tag = soup.find('script', string=lambda text: text and 'series' in text)

            if not script_tag:
                self.logger.error("未找到包含排行榜數據的script標籤")
                return ranking_data
            
            start_index = script_tag.string.index('series:') + len('series: ')
            end_index = script_tag.string.rindex(']') + 1
            series_data = script_tag.string[start_index:end_index]
            
            def replace_date_utc(match):
                params = match.group(1).split(', ')
                year = int(params[0])
                month = int(params[1])
                day = int(params[2])
                return f'"{year}-{month + 1:02d}-{day:02d}"'

            series_data = re.sub(r'Date\.UTC\((.*?)\)', replace_date_utc, series_data)
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
            self.logger.error(f"提取排行榜數據時出錯: {str(e)}")
            return []

    def get_bestsellers(self):
        """爬取暢銷榜資料"""
        soup = self._get_soup(self.base_url)
        if not soup:
            return []
            
        return self._extract_ranking_data(soup)

def main():
    base_url = "https://www.chimingpublishing.com/monster/book/0011001520"
    scraper = ChimingBestsellerScraper(base_url)
    bestsellers = scraper.get_bestsellers()
    
    if bestsellers:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        scraper.save_data(
            bestsellers,
            f'chiming_bestsellers_{timestamp}.json',
            format_type="json"
        )

if __name__ == "__main__":
    main() 