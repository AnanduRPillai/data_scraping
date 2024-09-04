import scrapy
from scrapy.http import Request
import json

class BhhsampSpider(scrapy.Spider):
    name = "bhhsamp"
    allowed_domains = ["bhhsamb.com"]
    start_urls = [
        'https://www.bhhsamb.com/CMS/CmsRoster/RosterSection?layoutID=963&pageSize=10&pageNumber=1&sortBy=random'
    ]
    agent_count = 0
    max_agents = 1120

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

    def start_requests(self):
        yield Request(
            url=self.start_urls[0],
            headers=self.headers,
            callback=self.parse,
            meta={'page': 1}
        )

    def parse(self, response):
        page = response.meta.get('page')
        agent_links = response.xpath('//a[@class="cms-int-roster-card-image-container site-roster-card-image-link"]//@href').extract()
        for link in agent_links:
            if self.agent_count < self.max_agents:
                agent_url = response.urljoin(link)
                yield Request(agent_url, callback=self.parse_agent, headers=self.headers)
            else:
                break

        page += 1
        next_page = f'https://www.bhhsamb.com/CMS/CmsRoster/RosterSection?layoutID=963&pageSize=10&pageNumber={page}&sortBy=random'
        if self.agent_count < self.max_agents:
            yield Request(next_page, headers=self.headers, meta={'page': page}, callback=self.parse)

    def parse_agent(self, response):
        name = response.xpath('//p[@class="rng-agent-profile-contact-name"]/text()').get(default='').strip()
        image_url = response.xpath('//article[@class="rng-agent-profile-main"]//img//@src').get(default='')
        phone_number = response.xpath('//ul//li[@class="rng-agent-profile-contact-phone"]//a//text()').get(default='').strip()

        address_parts = response.xpath('//ul//li[@class="rng-agent-profile-contact-address"]//text()').getall()
        address = ', '.join(part.strip() for part in address_parts if part.strip()).replace('\r\n', '').replace('\n', '').replace('\r', '')

        social_links = {
            'facebook': response.xpath('//li[@class="social-facebook"]//a/@href').get(default=None),
            'twitter': response.xpath('//li[@class="social-twitter"]//a/@href').get(default=None),
            'linkedin': response.xpath('//li[@class="social-linkedin"]//a/@href').get(default=None),
            'youtube': response.xpath('//li[@class="social-youtube"]//a/@href').get(default=None),
            'pinterest': response.xpath('//li[@class="social-pinterest"]//a/@href').get(default=None),
            'instagram': response.xpath('//li[@class="social-instagram"]//a/@href').get(default=None),
        }

        description = response.xpath('//article[@class="rng-agent-profile-content"]//span/text()').get(default='').strip()

        agent_data = {
            'name': name,
            'image_url': image_url,
            'phone_number': phone_number,
            'address': address,
            'description': description,
            'social_links': {key: value for key, value in social_links.items() if value}
        }

        with open('agents_data.jsonl', 'a') as file:
            file.write(json.dumps(agent_data, separators=(',', ':')) + '\n')

        self.agent_count += 1
        if self.agent_count >= self.max_agents:
            self.crawler.engine.close_spider(self, 'Reached the target number of agents')
