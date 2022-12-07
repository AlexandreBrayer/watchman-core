import scrapy
import json
from pydispatch import dispatcher
from scrapy import signals
import sys

class Bazarchic(scrapy.Spider):
    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    name = "Bazarchic"
    processId = "63852c7e3ce5b10a25d911d7"
    bodyForSalesId = {"operationName":"getSalesByUniverse","variables":{"salesByUniverseUniverse":"ACCUEIL","salesByUniverseDate":"","salesByUniversePagination":{"first":1000}},"query":"query getSalesByUniverse($salesByUniverseUniverse: String, $salesByUniversePagination: PaginationInput, $salesByUniverseDate: String, $salesByUniverseNewSalesOnly: Boolean) {\n  salesByUniverse(universe: $salesByUniverseUniverse, pagination: $salesByUniversePagination, date: $salesByUniverseDate, newSalesOnly: $salesByUniverseNewSalesOnly) {\n    totalCount\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    edges {\n      cursor\n      node {\n        id\n        name\n        rootId\n        isOpen\n        isOpenVip\n        coverUrl\n        coverLogoUrl\n        logoUrl\n        endDateTime\n        startDateTime\n        isLastingSale\n        position\n        hasWine\n        promoCategory\n        promoMulti\n        saleType\n        saleTargets\n        stickersDatas {\n          id\n          position\n          url\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}
    bodyForSaleInfos = {"operationName":"SaleProductsList","variables":{"saleId":"2452694","sort":"RELEVANCE","facetFilters":[],"filters":{"withVipProducts":None},"pagination":{"first":10000}},"query":"query SaleProductsList($saleId: ID!, $sort: SortEnum, $facetFilters: [FacetInput], $filters: FiltersInput, $pagination: PaginationInput) {\n  products: productsBySaleId(saleId: $saleId, sort: $sort, facetFilters: $facetFilters, filters: $filters, pagination: $pagination) {\n    totalCount\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    edges {\n      cursor\n      node {\n        ...InfoProduct\n        hasStock\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment InfoProduct on Product {\n  id\n  rangeId\n  groupId\n  ecoResponsibleLabel {\n    hasEcoResponsibleLabel\n    facetEcoResponsibleLabel\n    __typename\n  }\n  sizeDatas {\n    productId\n    stock\n    size\n    maxQuantity\n    sellPrice\n    publicPrice\n    __typename\n  }\n  imagesDatas {\n    urlListPage\n    __typename\n  }\n  title\n  sellPrice\n  publicPrice\n  appliedPrice\n  brandDatas {\n    id\n    name\n    __typename\n  }\n  unsuitableForUnderaged\n  saleId\n  isTissue\n  availableQuantity {\n    quantity\n    sizeId\n    __typename\n  }\n  __typename\n}\n"}
    bodyForProductInfos = {"operationName":"productInformation","variables":{"id":"4302929"},"query":"query productInformation($id: ID!) {\n  product: productById(id: $id) {\n    id\n    groupId\n    title\n    sellPrice\n    publicPrice\n    description\n    technicalSpecification\n    unsuitableForUnderaged\n    publicPriceYear\n    deliveryCondition\n    appliedPrice\n    ecoResponsibleLabel {\n      hasEcoResponsibleLabel\n      facetEcoResponsibleLabel\n      labels {\n        id\n        title\n        description\n        __typename\n      }\n      __typename\n    }\n    brandDatas {\n      id\n      logo\n      description\n      name\n      sizeGuide\n      showDatas\n      __typename\n    }\n    isTissue\n    availableQuantity {\n      quantity\n      sizeId\n      __typename\n    }\n    saleId\n    sizeDatas {\n      productId\n      maxQuantity\n      size\n      stock\n      sellPrice\n      publicPrice\n      __typename\n    }\n    hasStock\n    imagesDatas {\n      urlListPage\n      urlZoomDetailPage\n      __typename\n    }\n    __typename\n  }\n  productRecommended: recommendedProducts(productId: $id) {\n    id\n    saleId\n    title\n    sellPrice\n    publicPrice\n    ...EcoResponsability\n    imagesDatas {\n      urlListPage\n      __typename\n    }\n    brandDatas {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment EcoResponsability on Product {\n  ecoResponsibleLabel {\n    hasEcoResponsibleLabel\n    __typename\n  }\n  __typename\n}\n"}
    products = []

    def start_requests(self):
        yield scrapy.Request(url="https://services-fr.bazarchic.com/gateway/graphql", method="POST", body=json.dumps(self.bodyForSalesId), callback=self.parseSalesId)
    
    def parseSalesId(self, response):
        salesId = json.loads(response.body)["data"]["salesByUniverse"]["edges"]
        salesId = [x['node']['id'] for x in salesId]
        for i in salesId:
            self.bodyForSaleInfos["variables"]["saleId"] = i
            yield scrapy.Request(url="https://services-fr.bazarchic.com/gateway/graphql", method="POST", body=json.dumps(self.bodyForSaleInfos), callback=self.parseProducts)
    
    def parseProducts(self, response):
        products = json.loads(response.body)["data"]["products"]["edges"]
        for i in products:
            self.bodyForProductInfos["variables"]["id"] = i["node"]["id"]
            yield scrapy.Request(url="https://services-fr.bazarchic.com/gateway/graphql", method="POST", body=json.dumps(self.bodyForProductInfos), callback=self.parseProduct)

    def parseProduct(self, response):
        product = json.loads(response.body)["data"]["product"]
        self.products.append({
            "name": product["title"],
            "ref": "bazarchic_id_" + product["id"],
            "desc" : product["description"],
            "images" : [x["urlListPage"] for x in product["imagesDatas"]],
            "price" : product["publicPrice"],
            "reducedPrice" : product["sellPrice"],
            "url": "",
            "brand" : product["brandDatas"]["name"],
            "currency": "EUR",
            "from": self.processId,
        })
    
    def spider_closed(self, spider):
        print(json.dumps(self.products))
        sys.stdout.flush()
