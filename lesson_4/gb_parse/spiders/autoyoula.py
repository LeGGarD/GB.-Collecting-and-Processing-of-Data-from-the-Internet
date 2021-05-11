import scrapy
import pymongo
import re


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector_str, callback):
        for itm in response.css(selector_str):
            url = itm.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink",
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, ".Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu.blackLink",
            self.car_parse,
        )

    def car_parse(self, response):
        print(1)
        # Чего-то туплю, как по-другому словарь характеристик сделать... Не могу через генератор...
        specs = {}
        for el in response.css(".AdvertSpecs_row__ljPcX"):
            key = el.css(".AdvertSpecs_label__2JHnS::text").extract_first()
            value = el.css(".AdvertSpecs_data__xK2Qx a::text").extract_first()
            if value is None:
                value = el.css(".AdvertSpecs_data__xK2Qx::text").extract_first()
            specs[key] = value

        # Основные данные
        data = {
            "url": response.url,
            "title": response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
            # Список фото объявления(ссылки)
            "photo": [itm.attrib.get("src") for itm in response.css("figure.PhotoGallery_photo__36e_r img")],
            # Список характеристик
            "specifications": specs,
            # Описание объявления
            "description": response.css(".AdvertCard_descriptionInner__KnuRi::text").extract_first(),
            # ссылка на автора объявления
            "author_url": AutoyoulaSpider.get_author_id(response),
        }

        # Сохраняем в монго
        self.db_client["autoyoula_parse"][self.name].insert_one(data)

    # находил ссылку на автора, но уже посмотрел начало пятого урока, так что оставлю этот метод тут)
    @staticmethod
    def get_author_id(resp):
        marker = "window.transitState = decodeURIComponent"
        for script in resp.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (
                        resp.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass