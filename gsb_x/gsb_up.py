API_KEY='AIzaSyBPSJPgWLgul_UUZkvrYQwIlBPgwr22FZQ'

import hashlib
import urllib
# import urllib2
import urllib.request
import urllib.error
from urllib.parse import urlparse
# from urlparse import urlparse

sha256 = hashlib.sha256()


def validate_url(url):
    if "http://" in url:
        url = url.replace("http://", "")
    if url[-1] != "/":
        url += "/"
    return url


def recursive_url_build(url):
    result_combinations_list = []
    url_obj = urlparse("http://"+url)
    data_parts = url_obj.query
    paths = url_obj.path

    def construct_url_combinations(current_url):
        url_obj = urlparse("http://"+current_url)
        path_parts = url_obj.path
        domain_parts = url_obj.netloc
        path_explode = path_parts.split('/')
        path_explode = path_explode[1:]
        if path_explode != ['']:
            for item in path_explode:
                if item == '':
                    path_explode.pop(path_explode.index(item))
        domain_parts += "/"
        for path in path_explode:
            if "." in path:
                domain_parts += path
            elif path_parts == "/":
                domain_parts = domain_parts
            else:
                domain_parts += path + "/"
            result_combinations_list.append(domain_parts)

        tmp = url_obj.netloc
        len_of_domain = len(tmp.split("."))
        domain_explode = current_url.split('.', 1)
        if len_of_domain > 2:
            construct_url_combinations(domain_explode[1])

    construct_url_combinations(url)

    if data_parts != '':
        data_part_appendix = []
        for item in result_combinations_list:
            if not item.endswith("/"):
                data_part_appendix.append(item+"?"+data_parts)
            elif paths == "/":
                data_part_appendix.append(item+"?"+data_parts)
        return result_combinations_list+data_part_appendix
    else:
        return result_combinations_list


def hashify_list(list_to_hashify):
    new_list = []
    for item in list_to_hashify:
        new_item = hashlib.sha256()
        new_item.update(item)
        new_list.append(new_item.digest()[:4])
    return new_list


def get_red_page_result(url="", proxies=None, verify=False, chrome_version='40.0.2214.115'):
    url = validate_url(url)
    list_of_url_combos = recursive_url_build(url)
    print (str(list_of_url_combos))
    print (url)
    if url not in str(list_of_url_combos):
        list_of_url_combos.append(url[:url.index('/')+1])
    print (str(list_of_url_combos))
    hash_list = hashify_list(list_of_url_combos)
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'text/plain',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36' % chrome_version,
        'Accept-Encoding': 'gzip, deflate',
    }

    data = "4:"+str(4*len(hash_list))+"\n"+"".join(hash_list)

    params = {'client': 'googlechrome',
              'appver': chrome_version,
              'pver': 3.0,
              'key': API_KEY}

    method = 'POST'
    handler = urllib2.HTTPHandler()
    opener = urllib2.build_opener(handler)
    request = urllib2.Request('https://safebrowsing.google.com/safebrowsing/gethash?' + urllib.urlencode(params),
                              data,
                              headers)

    request.get_method = lambda: method
    try:
        connection = opener.open(request)
    except urllib2.HTTPError as e:
        connection = e

    if connection.code == 200:
        response = connection.read()
        print (response)
        if "goog-unwanted-shavar" in response.lower():
            # If red page presented - returns True
            return {"result": True}
        elif "malware" in response.lower():
            return {"result": True}
        elif "badbinurl" in response.lower():
            return {"result": True}
        elif "phish" in response.lower():
            return {"result": True}
        else:
            return {"result": False}
    else:
        return {"result": "error fetching result"}


def check_red_screen(event, context):
    return get_red_page_result(url=event['url'])

# print (check_red_screen({'url': URL_TO_TEST}, ''))

t2='http://kindlevod.ru/'

print (check_red_screen({'url': t2}, ''))