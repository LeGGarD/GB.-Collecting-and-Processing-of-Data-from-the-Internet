import json
import requests
import time
from pathlib import Path
from urllib.parse import urlparse

"""
Задача - организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы

результат: 
Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json файлы. 
Для каждой категории товаров должен быть создан отдельный файл
и содержать товары исключительно соответсвующие данной категории.

пример структуры данных для файла:
{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""


class Parse5ka_homework:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    params = {
        "records_per_page": 20
    }

    def __init__(self, prod_url: str, cat_url: str, save_path_prod: Path, save_path_cats: Path):
        self.prod_url = prod_url
        self.cat_url = cat_url
        self.save_path_prod = save_path_prod
        self.save_path_cats = save_path_cats

    # сохранятор с ensure_ascii и utf-8 кодировкой, чтобы не падал скрипт на кривых символах
    def _save(self, data: dict, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    # парсер продуктов. Берет гет запрос по функции, меняет юрл на некст, если некст юрл None - заканчивает парсинг
    # если нет - йилдит значения data['results']
    def _parse(self, url: str):
        while url:
            response = self._get_response_prods(url)
            data = response.json()
            url = data["next"]
            for product in data['results']:
                yield product

    # запрос продуктов. По какой-то причине next ссылки в апи указаны с другим нетлоком, поэтому это надо исправлять
    # дальше гет запрос с хедером, юзер-агент как браузер. Если статус запроса ОК - возвращает запрос
    def _get_response_prods(self, url, *args, **kwargs):
        while True:
            url = url.replace(urlparse(url).netloc, urlparse(self.prod_url).netloc)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(3)

    # запрос категорий. Тут вывод - это сразу json() данные
    def _get_response_cats(self, url, *args, **kwargs):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data
            time.sleep(3)

    # итерируемся по всем категориям по очереди. Задаем параметры для ссылки дальше. Формируем новую ссылку, которая
    # выведет продукты только нужной нас категории. Создаем список в категории, экстендим его результатами парсинга
    # продуктов. Задаем путь для сохранения, название - айди категории. Сохраняем данные
    def run(self):
        for category in self._get_response_cats(self.cat_url):
            params = f"?categories={category['parent_group_code']}"
            url = f"{self.prod_url}{params}"

            category['products'] = []
            category['products'].extend(list(self._parse(url)))

            file_path = self.save_path_cats.joinpath(f"{category['parent_group_code']}.json")
            self._save(category, file_path)


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == '__main__':
    save_path_prod = get_save_path("products")
    save_path_categories = get_save_path("categories")
    prod_url = 'https://5ka.ru/api/v2/special_offers/'
    cat_url = 'https://5ka.ru/api/v2/categories/'
    parser = Parse5ka_homework(prod_url, cat_url, save_path_prod, save_path_categories)
    parser.run()
