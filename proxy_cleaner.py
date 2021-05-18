import socket
import urllib.request
import urllib.error

socket.setdefaulttimeout(180)

proxy_list = []

with open("proxies.txt") as f:
    for line in f:
        proxy_list.append(line)

print(f"there are {len(proxy_list)} proxies in the file")


def is_bad_proxy(pip):
    try:
        proxy_handler = urllib.request.ProxyHandler({'http': pip})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        sock = urllib.request.urlopen('http://www.google.com')  # change the url address here
        # sock=urllib.urlopen(req)
    except urllib.error.HTTPError as e:
        print('Error code: ', e.code)
        return e.code
    except Exception as detail:

        print("ERROR:", detail)
        return 1
    return 0


for item in proxy_list:
    if is_bad_proxy(item):
        print("Bad Proxy", item)
        proxy_list.remove(item)
    else:
        print(item, "is working")

with open('proxies_cleared.txt', 'w') as f:
    for proxy in proxy_list:
        f.write(proxy)