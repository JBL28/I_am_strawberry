# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from typing import Iterable
import scrapy
from scrapy import Spider, Selector
from bs4 import BeautifulSoup
import requests
from .. import items
import re



class evalspider(Spider):
    name = "make_eval"

    def start_requests(self):
        url ="https://www.nongsaro.go.kr/portal/ps/pss/pssb/ncpmsConsultLst.ps?menuId=PS65440"
        yield scrapy.Request(url, self.parse_start)
    

    def parse_start(self, reponse):
        index_urls = [
            "https://www.nongsaro.go.kr/portal/ps/pss/pssb/ncpmsConsultLst.ps?menuId=PS65440&pageIndex=1&dgnssReqNo=0&sRealmCode=&sSidoCode=&sSigunguCode=&srchStr=%EB%94%B8%EA%B8%B0",
            "https://www.nongsaro.go.kr/portal/ps/pss/pssb/ncpmsConsultLst.ps?menuId=PS65440&pageIndex=2&dgnssReqNo=0&sRealmCode=&sSidoCode=&sSigunguCode=&srchStr=%EB%94%B8%EA%B8%B0",
            "https://www.nongsaro.go.kr/portal/ps/pss/pssb/ncpmsConsultLst.ps?menuId=PS65440&pageIndex=3&dgnssReqNo=0&sRealmCode=&sSidoCode=&sSigunguCode=&srchStr=%EB%94%B8%EA%B8%B0",
            "https://www.nongsaro.go.kr/portal/ps/pss/pssb/ncpmsConsultLst.ps?menuId=PS65440&pageIndex=4&dgnssReqNo=0&sRealmCode=&sSidoCode=&sSigunguCode=&srchStr=%EB%94%B8%EA%B8%B0"
            ]
        fncDtl_numbers = []
        
        for url in index_urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # li 태그 내의 a 태그에서 javascript 코드 추출
            li_tags = soup.select('#srchFm div ul li a')
            
            for tag in li_tags:
                onclick_text = tag.get('onclick')
                if onclick_text:
                    # JavaScript 함수 호출에서 num 값 추출
                    match = re.search(r"fncDtl\('(\d+)'\)", onclick_text)
                    if match:
                        fncDtl_numbers.append(match.group(1))
        
        for num in fncDtl_numbers:
            content_urls = 'https://www.nongsaro.go.kr/portal/ps/pss/pssb/ncpmsConsultDtl.ps?menuId=PS65440&pageIndex=2&dgnssReqNo='+num+'&sRealmCode=&sSidoCode=&sSigunguCode=&srchStr=%EB%94%B8%EA%B8%B0'
            yield scrapy.Request(content_urls, self.parse_items)
        

    def parse_items(self, response):
        item = items.link_item()
        selector = Selector(text=response.text)
        title3_texts = selector.css('p.title3::text').getall()
        title = selector.css('#contentForm > div > div.board_view.spt > div:nth-child(1) > h3 > strong').getall()
        title3_text = [self.remove_escape_characters(text) for text in title3_texts]
        print(title3_text)

        item['title'] = title
        item['input_text'] = title3_text[0] if len(title3_text) > 0 else ''
        item['expert_check'] = title3_text[1] if len(title3_text) > 1 else ''
        item['expert_answer'] = title3_text[2] if len(title3_text) > 2 else ''
    
        yield item

    def remove_escape_characters(self, text):
   
        clean_text = re.sub(r'\\[nrtbf\"\'\\]', '', text)
        return clean_text

    def HTML_tag_remover(a, HTML_syntax_list):
        
        """Removing HTML tags -- response.xpath().getall() -> [<class 'crawling.spiders.CrawlingSpider'>,<class 'list['string' ... ]'>]"""
        tag_pattern = re.compile('<.*?>')
        for i in range(0,len(HTML_syntax_list)):
            t = re.sub(tag_pattern, "", HTML_syntax_list[i])

            HTML_syntax_list[i] = t
        
        return HTML_syntax_list
