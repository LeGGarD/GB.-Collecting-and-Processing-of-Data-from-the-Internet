from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose


def get_params(data):
    data = [itm.replace(": ", "") for itm in data if (itm != ' ') and (itm != '\n  ')]
    data = [itm[:-1] if itm[-1] == ' ' else itm for itm in data]
    result = {}
    for idx in range(int(len(data) / 2)):
        result.update({data[idx * 2]: data[idx * 2 + 1]})
    return result


class AvitoLoader(ItemLoader):
    default_item_class = dict
    title_out = TakeFirst()
    cost_out = TakeFirst()
    address_out = TakeFirst()
    params_in = Compose(get_params)
    author_url_out = TakeFirst()
