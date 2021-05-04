import time # для задержек в гет запросах
import typing # для того, чтобы передавать и сохранять функции
import requests
from urllib.parse import urljoin # для легкой работы с юрлами
import bs4 # для парсинга HTML (конкретно в нашем случае пользуем lxml parser)

from database.database import Database


class GbBlogParse:
    def __init__(self, start_url, db):
        self.time = time.time()
        self.start_url = start_url
        self.db = db
        self.done_urls = set() # уникальные юрлы которые уже отработали
        self.tasks = [] # список тасков (функции, хранящие в себе parse_feed/parse_post, url + soup)
        start_task = self.get_task(self.start_url, self.parse_feed) # задает первую таску на старт юрл + парс фид
        self.tasks.append(start_task) # добавляем таск в список заданий
        # self.done_urls.add(self.start_url) # вроде как лишняя строчка

    # проверяет, новая ли ссылка, что передается. Если да - записывает в список пройденных и возвращает task
    # в котором остается parse_feed/parse_post, url + soup
    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return lambda *_, **__: None
        self.done_urls.add(url)
        return task

    # с задержкой делает гет реквест + принтит пройденный юрл
    def _get_response(self, url, *args, **kwargs):
        if self.time + 0.9 < time.time():
            time.sleep(0.5)
        response = requests.get(url, *args, **kwargs)
        self.time = time.time()
        print(url)
        return response

    # берет суп по юрлу, через lxml парсер
    def _get_soup(self, url, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    # создает сет ссылок генератором, через urljoin, каждую ссылку передает в гет_таск и добавляет в список тасков
    def task_creator(self, url, tags_list, callback):
        links = set(
            urljoin(url, itm.attrs.get("href")) for itm in tags_list if itm.attrs.get("href")
        )
        for link in links:
            task = self.get_task(link, callback)
            self.tasks.append(task)

    # итерируемся по фид странцие. Сначала по ссылкам пагинации, потом по каждому посту.
    # все ссылки передаем в таск криэйтор, чтобы тот напихал их в список тасков
    def parse_feed(self, url, soup):
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(url, ul_pagination.find_all("a"), self.parse_feed)
        # post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        # self.task_creator(
        #     url, post_wrapper.find_all("a", attrs={"class": "post-item__title"}), self.parse_post
        # )
        posts = soup.find_all('a', attrs={'class': 'post-item__title'})
        self.task_creator(url, posts, self.parse_post)

    # посредством махинаций с супом формируется и возвращается json данных, какого угодно наполнения
    def parse_post(self, url, soup):
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        data = {
            "post_data": {
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "url": url,
                "id": soup.find("comments").attrs.get("commentable-id"),
            },
            "author_data": {
                "url": urljoin(url, author_tag.parent.attrs.get("href")),
                "name": author_tag.text,
            },
            "tags_data": [
                {"name": tag.text, "url": urljoin(url, tag.attrs.get("href"))}
                for tag in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self._get_comments(soup.find("comments").attrs.get("commentable-id")),
        }
        return data

    # формирует апи для комментов, берет гет запрос по апи, результат запихивает в дату и возвращает его
    def _get_comments(self, post_id):
        api_path = f"/api/v2/comments?commentable_type=Post&commentable_id={post_id}&order=desc"
        response = self._get_response(urljoin(self.start_url, api_path))
        data = response.json()
        return data

    # итерируется по списку задач, записывая результат выполнения каждой в переменную.
    # Если результат словарь - вызывает метод сейв
    def run(self):
        for task in self.tasks:
            task_result = task()
            if isinstance(task_result, dict):
                self.save(task_result)

    # сохраняет словарь данных (json) в коллекцию монго
    def save(self, data):
        self.db.add_post(data)


if __name__ == '__main__':
    # collection = MongoClient()["gb_parse_20_04"]["gb_blog"]
    db = Database("sqlite:///gb_blog.db")
    parser = GbBlogParse("https://gb.ru/posts", db)
    parser.run()
