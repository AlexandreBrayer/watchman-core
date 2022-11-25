import sys
from scrapy.crawler import CrawlerProcess
from lib.thebradery import TheBradery

spiderTable = {
    "4n6mcbl33nhropd": TheBradery,
}

for arg in sys.argv[1:]:
    process = CrawlerProcess()
    process.crawl(spiderTable[arg])
    
process.start()