import scrapy


class BhhsambSpider(scrapy.Spider):
    name = "bhhsamb"
    allowed_domains = ["www.bhhsamb.com"]
    start_urls = ["https://www.bhhsamb.com/agents"]

    def parse(self, response):
        pass
