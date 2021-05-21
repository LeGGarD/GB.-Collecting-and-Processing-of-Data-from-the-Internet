FEED_SELECTORS = {
    # 'start': '//li[@data-marker="category[1000030]"]//a/@href',
    'pagination': '//div[contains(@class, "pagination-hidden-3jtv4")]//a[contains(@class, "pagination-page")]/@href',
    'post': '//div[contains(@class, "iva-item-titleStep-2bjuh")]//a[@data-marker="item-title"]/@href',
}
DATA_SELECTORS = {
    'title': '//h1[contains(@class, "title-info-title")]//span/text()',
    'cost': '//span[@itemprop="price"]/@content',
    'address': '//span[contains(@class, "item-address__string")]/text()',
    'params': '//ul[contains(@class, "item-params-list")]/li[contains(@class, "item-params-list-item")]//text()',
    'author_url': '(//div[contains(@class, "seller-info-avatar")]//a/@href)[1]',
}