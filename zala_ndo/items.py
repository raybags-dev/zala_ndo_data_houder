import scrapy


class ZalaNdoItem(scrapy.Item):
    uuid = scrapy.Field()
    name = scrapy.Field()
    colour = scrapy.Field()
    image = scrapy.Field()
    manufacturer = scrapy.Field()
    sku = scrapy.Field()
    description = scrapy.Field()
    variant_sku = scrapy.Field()
    availability = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    product_id = scrapy.Field()
