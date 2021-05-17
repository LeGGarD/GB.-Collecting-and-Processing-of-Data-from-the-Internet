import scrapy
import pymongo
from ..loaders import HeadhunterLoader


class HeadhunterSpider(scrapy.Spider):
    name = "headhunter"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    _xpath_selectors = {
        'vacancy': '//span[@data-qa="bloko-header-3"]//a/@href',
        'pagination': '//div[contains(@class, "bloko-gap bloko-gap_top")]//a[@data-qa="pager-page"]/@href',
    }
    _xpath_data_selectors = {
        'title': '//h1[@data-qa="vacancy-title"]/text()',
        'salary': '//div[contains(@class, "vacancy-title")]//span/text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="bloko-tag-list"]//'
                  'div[contains(@data-qa, "skills-element")]/'
                  'span[@data-qa="bloko-tag__text"]/text()',
        "author": '//a[@data-qa="vacancy-company-name"]/@href',
    }
    _xpath_author_data_selectors = {
        'author_url': '',
        'author_name': '',
        'author_website': '',
        'author_field_of_activity': '',
        'author_description': '',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._xpath_selectors['pagination'], self.parse
        )
        yield from self._get_follow(
            response, self._xpath_selectors['vacancy'], self.vacancy_parse
        )

    def vacancy_parse(self, response, *args, **kwargs):
        loader = HeadhunterLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item
