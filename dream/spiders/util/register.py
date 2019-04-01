# -*- coding: utf-8 -*-

# Using Tor + Privoxy is advised, though the development of Polipo is discontinued, since direct connect
# to Tor with requests may cause some problems, for instance Connection Refused,
# which from my expierience are hard to avoid.
# 只用一个alt link 效果最佳！！！！！
import os
import requests
from lxml import html
from .captcha.predict import CaptchaSolver
import random
import string
from .log import logger
from tenacity import retry
from multiprocessing.dummy import Pool
import time
import base64
# This market is shutting down on 04/30/2019 and is transferring its services to a partner company, onion address: weroidjkazxqds2l.onion (currently offline, opening soon)

capsolver = CaptchaSolver()

path = os.path.dirname(__file__)
url_list = ['http://wxanv3mgclbfdt56n4zs2tpo62npcbheyfmb3wdfxzcz43rhvway7did.onion',
            'weroidjkazxqds2l.onion',
            'http://wdsgtsqkk5sk5zmqr4pc2lqdoxfwgrjvw2i55kloczhqq3nvr3bm3wyd.onion',
            'http://pjaopjqvjk6be4wz.onion'
            'http://jd6yhuwcivehvdt4.onion',
            'http://t3e6ly3uoif4zcw2.onion',
            'http://7ep7acrkunzdcw3l.onion',
            'http://vilpaqbrnvizecjo.onion',
            'http://igyifrhnvxq33sy5.onion',
            'http://6qlocfg6zq2kyacl.onion',
            'http://x3x2dwb7jasax6tq.onion',
            'http://bkjcpa2klkkmowwq.onion',
            'http://xytjqcfendzeby22.onion',
            'http://nhib6cwhfsoyiugv.onion',
            'http://k3pd243s57fttnpa.onion',
            'http://4hvmvhnqyeorgzlb.onion',
            'http://uhivlt5grrqjhad7.onion',
            'http://c6ctfwncts3auk4u.onion',
            'http://t5kqoucj5kbboheh.onion',
            'http://yq3fmhhpvfcfr2vg.onion',
            'http://4mtu5pl6yp3fmvny.onion',
            'http://4buzlb3uhrjby2sb.onion',
            'http://6khhxwj7viwe5xjm.onion',
            'http://jirdqewsia3p2prz.onion',
            'http://n3mvkmkqb3ry4rbb.onion',
            'http://e2rlc42c2hah6tgj.onion',
            'http://f6sfqkun24oteipd.onion',
            'http://hdx7ftyfbopx3tep.onion',
            'http://r72kzw55evvfi6cp.onion',
            'http://jo5jaiz6euzmno2b.onion',
            'http://6frnzrkfkoyyp2gk.onion',
            'http://ocan7onexbaad3g7.onion',
            'http://s2c4cmjtvqvdlpw4.onion',
            'http://2op42f4qv2reca5b.onion',
            'http://53tae27o6zd27rvf.onion',
            'http://lchudifyeqm4ldjj.onion']


url_list = ['http://wxanv3mgclbfdt56n4zs2tpo62npcbheyfmb3wdfxzcz43rhvway7did.onion']
proxy_dict = {'http': 'http://127.0.0.1:8118'}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0', 'Cache-Control': 'no-cache'}

def pingWorker(urlAlt):
    try:
        res = requests.get(url=urlAlt, proxies=proxy_dict, headers=headers, timeout=15)
    except:
        return urlAlt, 100
    if res.status_code == 200:
        print(urlAlt, res.elapsed.total_seconds())
        return urlAlt, res.elapsed.total_seconds()
    else:
        return urlAlt, 100

def pingServers():
    global url_list
    with Pool(32) as pool:
        newList = pool.map(pingWorker, url_list)
    results = []
    for i in newList:
        if i[1] <= 15:
            results.append(i[0])
    # url_list = results
    url_list = ['http://pjaopjqvjk6be4wz.onion']
    return url_list

@retry
def get_cookies():
    '''request captcha'''
    print('get_cookies')
    domain = random.choice(url_list)
    cap_get = domain + '/img/captcha2'
    cap_post = domain + '/verifyHuman2'
    print(cap_post)
    img_get_res = requests.get(url=cap_get, proxies=proxy_dict, headers=headers, timeout=15)
    print('Got Image', base64.b64encode(img_get_res.content))
    # solve cap
    form_data = {}
    form_data['captcha'] = cap_solve(img_get_res)
    # form_data['captcha'] = input('hello, pls input the solution:\n')
    form_data['Solve'] = 'Solve'
    # post captcha
    cap_post_res = requests.post(url=cap_post, data=form_data, proxies=proxy_dict, headers=headers, timeout=15)
    if cap_post_res.cookies:
        logger.info('Got first cookie')
        logger.info(cap_post_res.cookies.get_dict())
        # cookie_list.append(cap_post_res.cookies.get_dict())
        return cap_post_res
    else:
        raise IOError("Broken sauce, everything is hosed!!!")


def cap_solve(res=None):
    '''solve captcha image'''
    print('Solving captcha')
    if not os.path.exists(path+'/temp_img'):
        os.mkdir(path+'/temp_img')
    file_name = path + '/temp_img/' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) + '.jpeg'
    with open(file_name, 'wb') as c:
        c.write(res.content)
    sol = capsolver.SolveCaptcha(file_name)
    os.remove(file_name)
    return sol

@retry
def gen_cookies(captcha=None):
    '''Generate new cookies by submitting same captcha solution
        This is bizare but works!
    '''
    form_data = {}
    form_data['captcha'] = captcha
    form_data['Solve'] = 'Solve'
    while True:
        cap_post_res = requests.post(url=random.choice(url_list)+'/verifyHuman2', data=form_data, proxies=proxy_dict, headers=headers)
        cookie = cap_post_res.cookies.get_dict()
        if cookie:
            break
        else:
            logger.debug('Failed to generate')
    logger.info('New cookie generated: ' + str(cookie))
    return cookie

@retry
def try_login(data):
    '''
        wrap up func login() for Pool,  just to make it looks clear
        validates if a login attempt was success
    '''
    username = data[0]
    cookie = data[1]
    while True:
        res = login(username, cookie)
        tree = html.fromstring(res.content)
        banner = tree.xpath('.//a[@href="./profile"]/text()')
        if banner:
            logger.info('Login success: ' + username + str(cookie))
            if tree.xpath('.//div[@class="exchangeRateListing"]//a[contains(text(), "USD")]'):
                currency = tree.xpath('.//div[@class="exchangeRateListing"]//a[contains(text(), "USD")]/@href')[0].lstrip('.')
                requests.get(url=random.choice(url_list)+currency, cookies=cookie, proxies=proxy_dict, headers=headers)

            return cookie
        else:
            logger.error('Login failed: ' + username)

@retry
def login(username=None, cookie=None):
    '''
        organise the obfuscated login form &
        try to login with the generated cookies
    '''
    
    domain = random.choice(url_list)
    # get login page
    login_page = requests.get(url=domain, cookies=cookie, proxies=proxy_dict, headers=headers)
    tree = html.fromstring(login_page.content)
    ddos = tree.xpath('.//div[@class="ddos"]')
    if ddos:
        logger.error('Got DDos page??????')
        print(cookie, username)
        DDos_res = get_cookies()
        form_data = {}
        form_data['captcha'] = DDos_res.request.body.split('&')[0].split('=')[1]
        form_data['Solve'] = 'Solve'
        requests.post(url=random.choice(url_list)+'/verifyHuman2', data=form_data, cookies=cookie, proxies=proxy_dict, headers=headers)
        login_page = requests.get(url=domain, cookies=cookie, proxies=proxy_dict, headers=headers)
        tree = html.fromstring(login_page.content)

    form_data = {}
    data_invisible = tree.xpath('.//form//input[not(@value="")]')
    data_visible = tree.xpath('.//form//input[@value=""]')
    # Fill in username and pass
    for entry in data_visible:
            entry_name = entry.xpath('./@name')[0].strip()
            form_data[entry_name] = username
    captcha_entry_name = ''
    for entry in data_invisible:
        entry_title = entry.xpath('./@title')
        if entry_title:
            captcha_entry_name = entry.xpath('./@name')[0].strip()
        else:
            entry_name = entry.xpath('./@name')[0].strip()
            entry_value = entry.xpath('./@value')[0].strip()
            if entry_value not in form_data.values():
                form_data[entry_name] = entry_value
    img_uri = tree.xpath('.//form//img[@class="captcha3"]/@src')[0].strip()
    # get image
    img = requests.get(url=domain+'/'+img_uri, cookies=cookie, proxies=proxy_dict, headers=headers)
    form_data[captcha_entry_name] = cap_solve(img)
    # post login form
    login_res = requests.post(url=domain, data=form_data, cookies=cookie, proxies=proxy_dict, headers=headers)
    # return the response for submitting login form
    return login_res

def keep_alive(cookie=None):
    '''keep a cookie alive by simply requesting the front page'''
    domain = random.choice(url_list)
    res = requests.get(url=domain, cookies=cookie, proxies=proxy_dict, headers=headers)
    tree = html.fromstring(res.content)
    banner = tree.xpath('//a[@href="./profile"]/text()')
    print('keep_alive', banner, cookie)
# @retry
def initiate():
    start_time = time.time()
    pingServers()
    cookie_list = []
    login_list = []
    DDos_res = None
    with open(path+'/logins.txt') as logins:
        for l in logins:
            login_list.append(l.strip())
    del login_list[500:]
    # del login_list[5:]

    # get a captcha img and first cookie
    DDos_res = get_cookies()
    captcha_sol = DDos_res.request.body.split('&')[0].split('=')[1]
    # 修改为一个pool！！！！！
    # start generating cookies
    with Pool(128) as pool:
        cookie_list = pool.map(gen_cookies, [captcha_sol] * len(login_list))

    # login
    matched_list = list(zip(login_list, cookie_list))
    result = []
    with Pool(128) as pool:
        result = pool.map(try_login, matched_list)
    print(result)
    print("--- %s seconds ---" % (time.time() - start_time))
    
    return matched_list, url_list

def new_match(username=None):
    DDos_res = get_cookies()
    logger.info('Got NEW cookie')
    logger.info(DDos_res.cookies.get_dict())
    new_cookie = DDos_res.cookies.get_dict()
    data = username, new_cookie
    login_result = try_login(data)
    if login_result: print('New login pair generated!')
    return data

@retry
def register( cookie):
    form_data = {}
    domain = random.choice(url_list)
    # get login page
    register_page = requests.get(url=domain+'/register', cookies=cookie, proxies=proxy_dict, headers=headers)
    tree = html.fromstring(register_page.content)
    data_invisible = tree.xpath('.//form//input[not(@value="")]')
    data_visible = tree.xpath('.//form//input[@value=""]')
    usernameuser = ''
    for v in data_invisible:
        value_user = v.xpath('./@value')[0].strip()
        if all(not c.isdigit() and c.islower() for c in value_user) and len(value_user) > 6:
            usernameuser = value_user
            break
    for entry in data_visible:
            entry_name = entry.xpath('./@name')[0].strip()
            form_data[entry_name] = usernameuser

    for entry in data_invisible:
        entry_title = entry.xpath('./@title')
        if not entry_title:
            entry_name = entry.xpath('./@name')[0].strip()
            entry_value = entry.xpath('./@value')[0].strip()
            form_data[entry_name] = entry_value
        else:
            # captcha
            entry_name = entry.xpath('./@name')[0].strip()
            cap_res = requests.get(url=domain+'/img/captcha3', cookies=cookie, proxies=proxy_dict, headers=headers)
            form_data[entry_name] = cap_solve(cap_res)
            
    login_res = requests.post(url=domain+'/register', data=form_data, cookies=cookie, proxies=proxy_dict, headers=headers)
    return login_res

@retry
def try_register(cookie):
    while True:
        domain = random.choice(url_list)
        res = register(cookie)
        tree = html.fromstring(res.content)
        banner = tree.xpath('.//a[@href="./profile"]/text()')
        if banner:
            currency = tree.xpath('.//div[@class="exchangeRateListing"]//a[contains(text(), "USD")]/@href')[0].lstrip('.')
            currency_page = requests.get(url=domain+currency, cookies=cookie, proxies=proxy_dict, headers=headers)
            if currency_page.status_code == 200:
                success_usrname = banner[0].strip()
                with open('./logins2.txt', 'a') as log_file:
                    print(success_usrname)
                    log_file.write(success_usrname+'\n')
                    logger.info('Reg success: ' + banner[0].strip() + str(cookie))
                return success_usrname
        else:
            logger.error('Reg failed')

def reg_wraper(param):
    return try_register(gen_cookies(param))
# @retry
def auto_reg():
    pingServers()
    cookie_list = []
    usernames = []
    DDos_res = get_cookies()
    captcha_sol = DDos_res.request.body.split('&')[0].split('=')[1]
    # for i in range(0, 30):
    with Pool(32) as pool:
        pool.map(reg_wraper, [captcha_sol] * 1000)
        # 16线程每个线程获取100个cookies
        # with Pool(16) as pool:
        #     cookie_list = pool.map(gen_cookies, [captcha_sol] * 100)
        # with Pool(32) as pool:
        #     usernames = pool.map(try_register, cookie_list)


        # with open('./logins2.txt', 'a') as log_file:
        #     for u in usernames:
        #         print(u)
        #         log_file.write(u+'\n')

# auto_reg()
