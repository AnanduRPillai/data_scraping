import scrapy
import json
from scrapy.spiders import Spider
from scrapy.http import Request, FormRequest
headers = {'Accept': '*/*',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
           'Connection': 'keep-alive',
           'Host': 'www.bhhsamb.com',
           'Referer': 'https://www.bhhsamb.com/roster/Agents',
           'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
           'sec-ch-ua-mobile': '?0',
           'sec-ch-ua-platform': '"Linux"',
           'Sec-Fetch-Dest': 'empty',
           'Sec-Fetch-Mode': 'cors',
           'Sec-Fetch-Site': 'same-origin',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
           'X-Requested-With': 'XMLHttpRequest', }


class Bhhsamp(scrapy.Spider):
    name = "bhhsamp_"

    def start_requests(self):

        urls = 'https://www.bhhsamb.com/CMS/CmsRoster/RosterSection?layoutID=963&pageSize=10&pageNumber=1&sortBy=random'
        meta = {'page': 1}
        yield Request(urls, headers=headers,
                      meta=meta, callback=self.parse)

    def parse(self, response):
        page = response.meta.get('page')
        url_xpath = response.xpath(
            '//a[@class="site-roster-card-image-link"]//@href').extract()
        for p_url in url_xpath:
            # print(p_url)
            product_url = 'https://www.bhhsamb.com'+p_url
            yield Request(product_url,
                          callback=self.parse_product)

        page += 1
        next_link = 'https://www.bhhsamb.com/CMS/CmsRoster/RosterSection?layoutID=963&pageSize=10&pageNumber=' + \
            str(page)+'&sortBy=random'
        print(next_link)
        if next_link:
            meta = {'page': page}
            yield Request(next_link, headers=headers, meta=meta,
                          callback=self.parse)

    def parse_product(self, response):
        name = response.xpath(
            '//p[@class="rng-agent-profile-contact-name"]/text()').extract_first('').strip()
        image_url = response.xpath(
            '//article[@class="rng-agent-profile-main"]//img//@src').get()
        phone_number = response.xpath(
            '//ul//li[@class="rng-agent-profile-contact-phone"]//a//text()').extract_first('').strip()

        address_xpath = response.xpath(
            '//ul//li[@class="rng-agent-profile-contact-address"]//text()').extract()
        address = [x.strip() for x in address_xpath if x.strip()]
        address = ''.join(address)
        dictionary = {'name': name, 'image_url': image_url,
                      'phone_number': phone_number, 'address': address}
        file = open('sample_data.json', 'a')
        file.write(json.dumps(dictionary) + '\n')
        file.close()
