# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# 크롤링해온후 데이터 처리

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class GetJsonPipeline:
    
    def process_item(self, item, spider):
        return item
