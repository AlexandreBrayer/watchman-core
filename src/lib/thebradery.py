import scrapy
import json
from pydispatch import dispatcher
from scrapy import signals
import sys

class TheBradery(scrapy.Spider):
    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    name = "The Bradery"
    processId = "63821ac7b3353ff3a8cc7ce5"
    start_urls = [
        "https://thebradery.com/collections"
    ]
    products = []

    def parse(self, response):
        ahrefs = response.css('a::attr(href)').extract()
        paths = [x for x in ahrefs if x.startswith("/collections/")]
        paths = list(set(paths))
        for path in paths:
            yield scrapy.Request(response.urljoin(path + "/products.json?view=metafields&limit=100000&page=1"), callback=self.parse_category)

    def parse_category(self, response):
        products = json.loads(response.body)
        for product in products["products"]:
            for sku in product["variants"]:
                self.products.append({
                    "name": product["title"],
                    "ref": sku["sku"],
                    "desc": product["body_html"],
                    "images": [x["src"] for x in product["images"]],
                    "price": product["variants"][0]["compare_at_price"] or product["variants"][0]["price"],
                    "reducedPrice": product["variants"][0]["price"],
                    "url": "https://thebradery.com/products/"+product["handle"],
                    "brand": product["vendor"],
                    "currency": "EUR",
                    "meta": {
                        "productType": product["product_type"],
                    },
                    "from" : self.processId,
                })

    def spider_closed(self, spider):
        print(json.dumps(self.products))
        sys.stdout.flush()