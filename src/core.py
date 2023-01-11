import sys
from scrapy.crawler import CrawlerProcess
from lib.thebradery import TheBradery
from lib.bazarchic import Bazarchic
from lib.lacoste import Lacoste
from lib.kikikickz import Kikikickz

spiderTable = {
    "63821ac7b3353ff3a8cc7ce5": TheBradery,
    "63852c7e3ce5b10a25d911d7": Bazarchic,
    "638e1dd7bb49205cbe876772": Lacoste,
    "63be8fc4bc73f6d57c55bb52": Kikikickz,
}

process = CrawlerProcess()
process.crawl(spiderTable[sys.argv[1]])
    
process.start()