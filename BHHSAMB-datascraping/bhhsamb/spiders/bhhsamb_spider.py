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
    name = "bhhsamp"
    allowed_domains = ["bhhsamb.com"]
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
        agent_links = response.xpath('//a[@class="site-roster-card-image-link"]/@href').extract()
        for link in agent_links:
            if self.agent_count < self.max_agents:
                yield response.follow(link, headers=headers, callback=self.parse_agent)
            else:
                break

        if self.agent_count < self.max_agents:
            page = response.meta.get('page', 1) + 1
            next_page = f'https://www.bhhsamb.com/CMS/CmsRoster/RosterSection?layoutID=963&pageSize=10&pageNumber={page}&sortBy=random'
            if agent_links:
                yield Request(next_page, headers=headers, meta={'page': page}, callback=self.parse)

    def parse_agent(self, response):
        name = response.xpath('//p[@class="rng-agent-profile-contact-name"]/text()').get(default='').strip()
        image_url = response.xpath('//article[@class="rng-agent-profile-main"]//img/@src').get()
        phone_number = response.xpath('//ul//li[@class="rng-agent-profile-contact-phone"]//a/text()').get(default='').strip()
        address_xpath = response.xpath('//ul//li[@class="rng-agent-profile-contact-address"]//text()').getall()
        address = ' '.join([x.strip() for x in address_xpath if x.strip()])
        description = response.xpath('//article[@class="rng-agent-profile-content"]//span/text()').get(default="").strip()
        facebook = response.xpath('//ul//li[@class="social-facebook"]//a/@href').get()
        twitter = response.xpath('//ul//li[@class="social-twitter"]//a/@href').get()
        linkedin = response.xpath('//ul//li[@class="social-linkedin"]//a/@href').get()
        youtube = response.xpath('//ul//li[@class="social-youtube"]//a/@href').get()
        pinterest = response.xpath('//ul//li[@class="social-pinterest"]//a/@href').get()
        instagram = response.xpath('//ul//li[@class="social-instagram"]//a/@href').get()

        agent_data = {
            'name': name,
            'image_url': image_url,
            'phone_number': phone_number,
            'address': address,
            'description': description if description else None,
            'Facebook': facebook if facebook else None,
            'twitter': twitter if twitter else None,
            'linkedin': linkedin if linkedin else None,
            'youtube': youtube if youtube else None,
            'pinterest': pinterest if pinterest else None,
            'instagram': instagram if instagram else None
        }

        
        logging.info(json.dumps(agent_data, separators=(',', ':')))

        
        with open('agents_data.json', 'a') as json_file:
            json.dump(agent_data, json_file, separators=(',', ':'))
            json_file.write('\n')

        
        csv_columns = ['name', 'image_url', 'phone_number', 'address', 'description', 'Facebook', 'twitter', 'linkedin', 'youtube', 'pinterest', 'instagram']
        with open('agents_data.csv', 'a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_columns, delimiter=',')
            if self.agent_count == 0:
                writer.writeheader()
            writer.writerow(agent_data)

        self.agent_count += 1
        if self.agent_count >= self.max_agents:
            self.crawler.engine.close_spider(self, 'Reached the target number of agents')
