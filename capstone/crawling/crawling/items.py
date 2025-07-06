# Define here the models for your scraped items
# 크롤링 해오는 데이터를 class로 받아옴
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    # 현장기술지원 개요 : tech_support_date - 일자, 장소
    tech_support_date = scrapy.Field()
    # 영농현황 : environment - 재배작물, 재배규모, 재배형태, 재배 배지경(토양영양성분)
    environment = scrapy.Field()
    # 농가 및 현장의견 : problem - 이상증상(발생시기, 발생증상, 문제점), 급액 방법
    customer_problem = scrapy.Field()
    # 현장 조사 결과 : investigation - 현장 방문일시, 이상증상, 지상부 생육상태, 시설환경관리, 병해발생상황,
    investigation = scrapy.Field()
    # 종합 검토 의견 : soultion
    solution = scrapy.Field()
    # 기술지도 방향 : tech_advice
    tech_advice = scrapy.Field()
