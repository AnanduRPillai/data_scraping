import scrapy
import json
import csv
import logging
from scrapy.http import Request, FormRequest
from scrapy.spiders import Spider

headers = {
    'Accept': '*/*',
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
    'X-Requested-With': 'XMLHttpRequest'
}

class BhhsampSpider(scrapy.Spider):
    name = "bhhsamp_"
    allowed_domains = ["www.bhhsamb.com"]
    start_urls = ['https://www.bhhsamb.com/CMS/CmsRoster/RosterSection?layoutID=963&pageSize=10&pageNumber=1&sortBy=random']
    agent_count = 0
    max_agents = 1120

    def start_requests(self):
        yield Request(
            url=self.start_urls[0],
            headers=headers,
            callback=self.parse,
            meta={'page': 1}
        )

    def parse(self, response):
        page = response.meta.get('page')
        url_xpath = response.xpath('//a[@class="site-roster-card-image-link"]//@href').extract()
        for p_url in url_xpath:
            if self.agent_count < self.max_agents:
                product_url = 'https://www.bhhsamb.com' + p_url
                yield Request(product_url, callback=self.parse_product)
            else:
                break

        page += 1
        next_link = f'https://www.bhhsamb.com/CMS/CmsRoster/RosterSection?layoutID=963&pageSize=10&pageNumber={page}&sortBy=random'
        if self.agent_count < self.max_agents:
            yield Request(next_link, headers=headers, meta={'page': page}, callback=self.parse)

    def parse_product(self, response):
        name = response.xpath('//p[@class="rng-agent-profile-contact-name"]/text()').extract_first('').strip()
        image_url = response.xpath('//article[@class="rng-agent-profile-main"]//img//@src').get()
        phone_number = response.xpath('//ul//li[@class="rng-agent-profile-contact-phone"]//a//text()').extract_first('').strip()

        address_xpath = response.xpath('//ul//li[@class="rng-agent-profile-contact-address"]//text()').extract()
        address = ''.join([x.strip() for x in address_xpath if x.strip()])

        facebook = response.xpath('//li[@class="social-facebook"]//a/@href').get()
        twitter = response.xpath('//li[@class="social-twitter"]//a/@href').get()
        linkedin = response.xpath('//li[@class="social-linkedin"]//a/@href').get()
        youtube = response.xpath('//li[@class="social-youtube"]//a/@href').get()
        pinterest = response.xpath('//li[@class="social-pinterest"]//a/@href').get()
        instagram = response.xpath('//li[@class="social-instagram"]//a/@href').get()

        agent_data = {
            'name': name,
            'image_url': image_url,
            'phone_number': phone_number,
            'address': address,
            'description': None,
            'Facebook': facebook if facebook else None,
            'twitter': twitter if twitter else None,
            'linkedin': linkedin if linkedin else None,
            'youtube': youtube if youtube else None,
            'pinterest': pinterest if pinterest else None,
            'instagram': instagram if instagram else None
        }

        with open('sample_data.json', 'a') as file:
            file.write(json.dumps(agent_data, separators=(',', ':')) + '\n')

        self.agent_count += 1
        if self.agent_count >= self.max_agents:
            self.crawler.engine.close_spider(self, 'Reached the target number of agents')

