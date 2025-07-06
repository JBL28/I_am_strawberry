# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class link_item(scrapy.Item):
    title = scrapy.Field()
    input_text = scrapy.Field()
    expert_check= scrapy.Field()
    expert_answer = scrapy.Field()
    