import requests
from lxml import html
import random
from tenacity import retry


url_list = ['http://wallst7xs4tepmvb.onion']
proxy_dict = {'http': 'http://127.0.0.1:8118'}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'}

def solve_cap(base64):
    return 'None'

@retry
def login(cookies, credentials):
    domain = random.choice(url_list)
    login_page = requests.get(url=domain + '/index', cookies=cookies, proxies=proxy_dict, headers=headers)
    tree = html.fromstring(login_page.content)
    form_entry_dict = {}
    form_entry_dict['form[username]'] = credentials[0] 
    form_entry_dict['form[password]'] = credentials[1]
    form_entry_dict['form[captcha]'] = solve_cap(tree.xpath('(.//img[@title="captcha"]/@src)[1]')[0])

    form_ele = tree.xpath('.//form[@class="login-form"]//*[@name]')
    for i in form_ele:
        name = i.xpath('./@name')
        if name == 'form[_token]':
            form_entry_dict[name] = i.xpath('./@value')
    form_entry_dict['form[extendForm]'] = 'on'
    form_entry_dict['form[language]'] = 'en'
    form_entry_dict['form[pictureQuality]'] = 0
    form_entry_dict['form[sessionLength]'] = 43200
    login_res = requests.post(url=domain + '/login', data=form_entry_dict, cookies=cookies, proxies=proxy_dict, headers=headers)
    login_res_html = html.fromstring(login_res.content)
    if not login_res_html.xpath('.//input[@name="tokenid"]'):
        raise IOError("Broken sauce, everything is hosed!!!")
    else: return 'ok'
