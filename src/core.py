import sys
from scrapy.crawler import CrawlerProcess
from lib.thebradery import TheBradery

spiderTable = {
    "63821ac7b3353ff3a8cc7ce5": TheBradery,
}

for arg in sys.argv[1:]:
    process = CrawlerProcess()
    process.crawl(spiderTable[arg])
    
process.start()