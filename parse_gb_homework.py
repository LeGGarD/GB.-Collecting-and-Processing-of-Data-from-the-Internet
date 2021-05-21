"""
Целый день вчера разбирал готовый пример парсера, как он работает и что использует, гуглил библиотеки, через дебагер
останавливался в разных моментах, пробовал крутить данные и переменные, с супом игрался и тд

Слишком комплексное и трудное решение, чтобы просто сходу понять логику парсера

В этом документе я написал уже все из памяти, только разок не мог понять, как в супе правильно теги по класу найти.
(надо было в attrs словарь запихнуть) И еще спутал find/find_all, не мог понять, почему у меня по сету итерация
не хочет идти

Парсер получился на 90% такой же как из задания. Зная крутой итоговый вариант, трудно что то от себя добавить,
что улучшило бы код. Тут одно крутое решение на другом, для меня разобравшево все с нуля тут все идеально...

Было бы у меня времени раза в 2 больше на эти задания, я бы хотел аналогисчный парсер для другого ресурса написать...
Но времени нет и рандомный ресурс скорее всего вызовет кучу проблем...

Но курс конечно супер информативный, это круто
"""
from pymongo import MongoClient
import requests
import bs4
import time
import typing
from urllib.parse import urljoin


class ParseGB:
    def __init__(self, start_url, collection):
        self.start_url = start_url
        self.collection = collection
        self.done_urls = set()
        self.tasks = []
        start_task = self.get_task(start_url, self.parse_feed)
        self.tasks.append(start_task)

    def _get_response(self, url: str, *args, **kwargs):
        time.sleep(0.5)
        response = requests.get(url, *args, **kwargs)
        if response.status_code == 200:
            print(url)
            return response

    def _get_soup(self, url: str, *args, **kwargs):
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, 'lxml')
        return soup

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_urls:
            return lambda *_, **__: None
        self.done_urls.add(url)
        return task

    def task_creator(self, url: str, soup, callback: typing.Callable):
        url_list = set(
            urljoin(url, new_url.attrs.get('href'))
            for new_url in soup
            if new_url.attrs.get('href')
        )

        for el in url_list:
            task = self.get_task(el, callback)
            self.tasks.append(task)

    def parse_feed(self, url: str, soup):
        pagination = soup.find('ul', 'gb__pagination')
        a_tags = pagination.find_all('a')
        self.task_creator(url, a_tags, self.parse_feed)
        posts = soup.find_all('a', attrs={'class': 'post-item__title'})
        self.task_creator(url, posts, self.parse_post)

    def parse_post(self, url, soup):
        data = {
            "id": soup.find('comments').attrs.get('commentable-id'),
            "url": url,
            "post_title": soup.find('h1', attrs={'class': 'blogpost-title'}).text,
            "post_pic": soup.find('img').attrs.get('src'),
            "post_date": soup.find('div', attrs={'class': 'blogpost-date-views'}).find('time').attrs.get('datetime'),
            "author_name": soup.find('div', attrs={'itemprop': 'author'}).text,
            "author_profile": urljoin(start_url, soup.find('div', attrs={'itemprop': 'author'}).parent.attrs.get('href')),
            "comments": self.get_comments(url, soup),
        }
        return data

    def get_comments(self, url, soup):
        commentable_id = soup.find('comments').attrs.get('commentable-id')
        api_url = f'https://gb.ru/api/v2/comments?commentable_type=Post&commentable_id={commentable_id}&order=desc'
        if self._get_response(api_url):
            comments = self._get_response(api_url).json()
            return comments
        else:
            return f"post doesn't have comments"

    def run(self):
        for task in self.tasks:
            result = task()
            if isinstance(result, dict):
                self.save(result)

    def save(self, data: dict):
        self.collection.insert_one(data)


if __name__ == '__main__':
    start_url = 'https://gb.ru/posts'
    collection = MongoClient()["les_2_homework"]["gb_parser"]
    parser = ParseGB(start_url, collection)
    parser.run()
