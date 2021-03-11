import scrapy

from scrapy.loader import ItemLoader

from ..items import CecroItem
from itemloaders.processors import TakeFirst


class CecroSpider(scrapy.Spider):
	name = 'cecro'
	start_urls = ['https://www.cec.ro/noutati']

	def parse(self, response):
		post_links = response.xpath('//div[@class="col-12 col-lg-6"]')
		for post in post_links:
			url = post.xpath('.//a[@class="views-more-link"]/@href').get()
			date = post.xpath('.//time/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//a[@rel="next"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="col-sm-auto col-10 product-title"]/text()').get()
		description = response.xpath('//div[@class="body-description"]//text()[normalize-space()] | //div[@class="col-12 col-md-10"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=CecroItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
