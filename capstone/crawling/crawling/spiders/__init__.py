# This package will contain the spiders of your Scrapy project
# 
# 크롤링할 데이터 코딩
# Please refer to the documentation for information on how to create and manage
# your spiders.


from typing import Iterable
import scrapy
import requests
from bs4 import BeautifulSoup
from scrapy import Spider
from .. import items
import re


class CrawlingSpider(Spider):
    name = "crawling"

    def start_requests(self):

        """# Seed url + page num -->  get pagenum's xpath
        2. page idx request (현재페이지)
        3. page idx iterate (페이지idx를 순회)
            3-1 page filtering (딸기 관련 사례) # Beautifulsoup이 더 찾기 간편(tr태그)
            3-2 get page url(딸기 관련 사례일시 urllist에 append)
        4. pagecrawling ()
        5. crawling 데이터 Chromadb에 업데이트"""
        tech_url = "https://www.nongsaro.go.kr/portal/ps/psz/psza/contentMain.ps?menuId=PS00077&pageIndex=1&pageSize=10&cntntsNo=&sType=sCntntsSj&sText="
        yield scrapy.Request(tech_url, self.parse_technical_support)
        

    def parse_technical_support(self, response):

        #   현장기술 지원 목록조회  http://api.nongsaro.go.kr/service/sptTchnlgySport/sptTchnlgySportList
        #   현장기술 지원 상세조회  http://api.nongsaro.go.kr/service/sptTchnlgySport/sptTchnlgySportView
        NONGSARO_API_LIST_URL = 'http://api.nongsaro.go.kr/service/sptTchnlgySport/sptTchnlgySportList'
        NONGSARO_API_KEY = '20240419GVBOL4DMJZSFIZ7GOKXRW'
        NONGSARO_API_ITEM_URL = "http://api.nongsaro.go.kr/service/sptTchnlgySport/sptTchnlgySportView"
        NONGSARO_SEARCH_URL = 'https://www.nongsaro.go.kr/portal/ps/psz/psza/contentSub.ps?menuId=PS00077&cntntsNo='

        #   목록조회 -> 리턴받은 객체의 키값(문서)-> 재검색하고 크롤링
        response = requests.get(NONGSARO_API_LIST_URL+"?apiKey="+NONGSARO_API_KEY+'&pageNo=1&searchtype=3&searchword=%EB%94%B8%EA%B8%B0&numOfRows=1000')
        response_xml_content = response.content

        soup = BeautifulSoup(response_xml_content, 'lxml-xml')

        for key in soup.find_all('cntntsNo'):
            url = NONGSARO_SEARCH_URL+key.text
            yield scrapy.Request(url, self.parse_items)


    def parse_items(self, response):
        item = items.CrawlingItem()
        #print("++++++++",response.xpath('//table/tr[1]/td[2]/text()').get())
        item['title'] = self.HTML_tag_remover(response.xpath('//*[@id="contentForm"]/div/div[1]/div[1]/h3/strong').getall())
        item['tech_support_date'] = self.HTML_tag_remover(response.xpath('//*[@id="pszaCont"]/div[1]').getall())
        item['environment'] = self.HTML_tag_remover(response.xpath('//*[@id="pszaCont"]/div[2]').getall())
        item['customer_problem'] = self.HTML_tag_remover(response.xpath('//*[@id="pszaCont"]/div[3]').getall())
        item['investigation'] = self.HTML_tag_remover(response.xpath('//*[@id="pszaCont"]/div[4]').getall())
        item['solution'] = self.HTML_tag_remover(response.xpath('//*[@id="pszaCont"]/div[5]').getall())
        item['tech_advice'] = self.HTML_tag_remover(response.xpath('//*[@id="pszaCont"]/div[6]').getall())
        
        yield item


    def HTML_tag_remover(a, HTML_syntax_list):
        
        """Removing HTML tags -- response.xpath().getall() -> [<class 'crawling.spiders.CrawlingSpider'>,<class 'list['string' ... ]'>]"""
        tag_pattern = re.compile('<.*?>')
        for i in range(0,len(HTML_syntax_list)):
            t = re.sub(tag_pattern, "", HTML_syntax_list[i])

            HTML_syntax_list[i] = t
        
        return HTML_syntax_list