import pymongo
import scrapy

from ..loaders import AvitoLoader
from ..xpaths import FEED_SELECTORS, DATA_SELECTORS


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["avito.ru"]
    start_urls = ["https://www.avito.ru/krasnodar/kvartiry/prodam-ASgBAgICAUSSA8YQ?cd=1"]
    # start_urls = ["https://www.avito.ru/krasnodar/nedvizhimost?cd=1"]
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en;q=0.5",
        "Connection": "keep-alive"
    }

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    # def start(self, response, *args, **kwargs):
    #     print(1)
    #     yield from self._get_follow(
    #         response, FEED_SELECTORS['start'], self.parse
    #     )

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, FEED_SELECTORS['pagination'], self.parse
        )
        yield from self._get_follow(
            response, FEED_SELECTORS['post'], self.post_parse
        )

    def post_parse(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in DATA_SELECTORS.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
