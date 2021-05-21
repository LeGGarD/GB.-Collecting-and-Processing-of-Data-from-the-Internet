import re

from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


class HeadhunterLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = Join()
    description_out = Join()
    author_out = TakeFirst()
