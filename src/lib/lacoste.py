import scrapy
import json
from pydispatch import dispatcher
from scrapy import signals
import sys
import chompjs

class Lacoste(scrapy.Spider):
    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    name = "Lacoste"
    processId = "638e1dd7bb49205cbe876772"

    base_urls = ["https://www.lacoste.com/fr/lacoste/femme", "https://www.lacoste.com/fr/lacoste/homme"]
    sub_paths = ["/chaussures", "/sport", "/accessoires", "/vetements", "/sacs-petite-maroquinerie"]

    products = []
    def start_requests(self):
        for base_url in self.base_urls:
            for sub_path in self.sub_paths:
                yield scrapy.Request(base_url + sub_path + "?page=1", callback=self.parse)

    def parse(self, response):
        product_urls = list(set(response.css("a.js-product-tile-link::attr(href)").extract()))
        for product_url in product_urls:
            yield scrapy.Request(product_url, callback=self.parse_product)
        last_pagination_item = response.css("a.pagination-item")[-1]
        maxPage = int(last_pagination_item.css("::text").extract_first())
        current_page = int(response.url.split("?")[1].split("=")[1])
        if current_page < maxPage:
            next_page_url = response.url.split("?")[0] + "?page=" + str(int(response.url.split("?")[1].split("=")[1]) + 1)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_product(self, response):
        script = response.css("script:contains('window.currentProduct = ')::text").extract_first()
        parsed = chompjs.parse_js_object(script)
        name = parsed["name"]
        ref = parsed["id"]
        desc = " ".join(parsed["description"]["blocks"][0]["texts"])
        desc += " ".join(parsed["description"]["blocks"][0]["list"])
        images = response.css("img.js-zoomable-img::attr(data-src)").extract()
        if len(images) == 0:
            images = response.css("img.js-zoomable-img::attr(src)").extract()
        images = ["https:" + image for image in images]
        price = response.css("div.js-pdp-price p::text").extract_first().replace("€", "").replace(",", ".")
        price = price.split("-")[-1]
        reducedPrice = price
        url = response.url
        brand = "Lacoste"
        currency = "EUR"
        product = {
            "name": name,
            "ref": ref,
            "desc": desc,
            "images": images,
            "price": price,
            "reducedPrice": reducedPrice,
            "url": url,
            "brand": brand,
            "currency": currency,
            "from": self.processId
        }
        self.products.append(product)
        

    def spider_closed(self, spider):
        print(json.dumps(self.products))
        sys.stdout.flush()