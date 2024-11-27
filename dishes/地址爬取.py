# -*- coding: utf-8 -*-
import requests
from lxml import etree
import time
import re
from fake_useragent import UserAgent
import pandas as pd
import random
import math
import urllib3

# 禁用 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)




x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率

# 获取商户名称和ID
result = []
ua = UserAgent()

detail_header = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9",
    "connection": "keep-alive",
    "cookie":"showNav=#nav-tab|0|1; navCtgScroll=300; _lxsdk_cuid=19237fabf66c8-071fef50227867-26001051-1bcab9-19237fabf66c8; _lxsdk=19237fabf66c8-071fef50227867-26001051-1bcab9-19237fabf66c8; _hc.v=3ad3b14e-d95e-3f51-285e-d888e5fcce87.1727516033; WEBDFPID=y75v84y6ywu552y0yu8u452x63x56v3980762uzuuv797958541zw727-2042876037302-1727516036816EKOESCKfd79fef3d01d5e9aadc18ccd4d0c95077509; ctu=5483ce84c2909393248edc3325ed53c8655fa979e2548b0c071fa8ff3478e00c; s_ViewType=10; cy=5; cye=nanjing; aburl=1; cityid=5; default_ab=shopList%3AA%3A5; ua=%E6%88%91%E4%B8%8D%E7%9F%A5%E9%81%93; qruuid=e48379f2-1211-417c-b55c-271fddc06c4e; dplet=ccebfc64dd54b42aed30704aaff6e7be; dper=02021421f3fe1a2079c821326a606e52d79965a014add67cfa3fafcf45712ec503e299e268dba5605dbdcd5f68118dccb983995077cf5db63173000000009824000086150be97811e0c3c4c5c96e071f04aa77b4de6547bb76dd164f89611581e344e41c5117acd2d22da1933e5c85242c72; ll=7fd06e815b796be3df069dec7836c3df; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1731327911,1731506072,1731593878,1731859035; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1731859035; HMACCOUNT=8179AD0C8BF17F83; _lxsdk_s=1933ad7af0d-35d-a4a-5a7%7C%7C21",
    "host": "www.dianping.com",
    "referer": "https://www.dianping.com/nanjing/ch10/g105",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}



review_header = {
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9"}


# 获取店家页面数据
def get_data(content, xpath, flag):
    items_html = etree.HTML(content)
    data = items_html.xpath(xpath)
    if flag == 'shopPer':
        # 提取数字部分
        match = re.search(r'\d+(\.\d+)?', data[0])
        if match:
            number = match.group()
            return number
        else:
            return "暂无信息"
    elif flag == 'score':
        score_all = []
        for i in data:
            # 提取数字部分
            match = re.search(r'\d+(\.\d+)?', i)
            if match:
                number = match.group()
                score_all.append(number)
            else:
                score_all.append("暂无信息")
        return score_all
    elif flag == 'phone':
        # 提取数字部分
        match = re.search(r'\d+(\.\d+)?', data[0])
        if match:
            number = match.group()
            return number
        else:
            return "暂无信息"
    return data[0]

# 腾讯获得经纬度
def get_location(keyword):
    url = "https://apis.map.qq.com/ws/place/v1/search?"
    params = {'keyword': keyword,
              'boundary': 'region(南京 ,0)',
              'key': "VF5BZ-YFRR5-FGRIV-IWPOS-MY7HF-I7FU6" ,
              'page_size': 10}
    html = requests.get(url=url, headers=review_header, params=params).json()

    # 火星坐标系转wgs1984坐标
    def gcj02towgs84(lng, lat):
        """
        GCJ02(火星坐标系)转GPS84
        :param lng:火星坐标系经度
        :param lat:火星坐标系纬度
        :return:
        """
        if out_of_china(lng, lat):
            return lng, lat
        dlat = transformlat(lng - 105.0, lat - 35.0)
        dlng = transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * pi
        magic = math.sin(radlat)
        magic = 1 - ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]

    def transformlat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
              0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * pi) + 40.0 *
                math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
                math.sin(lat * pi / 30.0)) * 2.0 / 3.0
        return ret

    def transformlng(lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
              0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
                math.sin(2.0 * lng * pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * pi) + 40.0 *
                math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
                math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
        return ret

    def out_of_china(lng, lat):
        """
        判断是否在国内，不在国内不进行纠偏
        :param lng:
        :param lat:
        :return:
        """
        if lng < 72.004 or lng > 137.8347:
            return True
        if lat < 0.8293 or lat > 55.8271:
            return True
        return False

    return gcj02towgs84(html['data'][0]['location']['lng'], html['data'][0]['location']['lat'])


# 更换访问头直到返回正确数据
def scrapy(url, flag='', key_dict=''):
    try:
        if flag == 'star':
            # 请求并解析 JSON 数据
            response = requests.get(
                url=url,
                headers=detail_header,
                timeout=20,
                params=key_dict,
                verify=False
            )
            response.encoding = "utf-8"

            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                return None

            try:
                # 尝试解析 JSON
                tem_html = response.json().get('shopRefinedScoreValueList', None)
                if not tem_html:
                    print("Error: 'shopRefinedScoreValueList' not found in JSON")
                return tem_html
            except requests.exceptions.JSONDecodeError:
                print("Error: Response is not valid JSON")
                print("Response text:", response.text)
                return None

        # 请求并获取纯文本数据
        response = requests.get(
            url=url,
            headers=detail_header,
            verify=False
        )
        response.encoding = "utf-8"
        tem_html = response.text

        # 调试信息
        print("Response text:", tem_html)
        time.sleep(random.randint(0, 2) + random.random())

        # 检测验证中心
        if '验证中心' in tem_html:
            print(f"失败了,出现验证中心")
            time.sleep(2)  # 延迟重试
            return scrapy(url, flag, key_dict)  # 避免递归过深

        return tem_html

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

def getFoodShop():
    shop_name_tem = []
    # 爬取40页数据
    for index in range(3,4):
        print(f"第{index}页")
        items_shop_url = r'https://www.dianping.com/nanjing/ch10/r69p{page}'.format(page=index)
        content = scrapy(items_shop_url)
        items_html = etree.HTML(content)
        # 获取店名、id、图片
        shop_id = items_html.xpath(
            '//*[@id="shop-all-list"]//ul//li//a[@data-click-name="shop_title_click"]/@data-shopid')
        shop_name = items_html.xpath('//*[@id="shop-all-list"]//ul//li//a[@data-click-name="shop_title_click"]/@title')
        shop_img = items_html.xpath(
            '//*[@id="shop-all-list"]//ul//li//a[@data-click-name="shop_img_click"]/img/@data-src')
        for mixture in zip(shop_id, shop_name, shop_img):
            # 获取第一个店家详细信息
            info = {}
            info['id'] = mixture[0]
            info['shopname'] = mixture[1]
            info['shopimgs'] = mixture[2]
            # 访问详情页获取店家其他详细信息
            item_shop_url = r'https://www.dianping.com/shop/{id}'.format(id=mixture[0])
            shop_content = scrapy(item_shop_url)
            # 获取店家地址
            time.sleep(5)
            shopAddress = get_data(shop_content, '//*[@id="address"]/text()', 'address')
            info["address"] = shopAddress
            # 获取店家人均价格
            shopPer = get_data(shop_content, '//*[@id="avgPriceTitle"]/text()', 'shopPer')
            info["price"] = shopPer
            # 获取店家不同评分数据
            # 创建ajax链接
            shopId = info['id']
            try:
                mainCategoryId = eval(re.findall('mainCategoryId:(.*?),', shop_content)[0])
                cityId = int(eval(re.findall('cityId:(.*?),', shop_content)[0]))
                key_dict = {"shopId": shopId, "mainCategoryId": mainCategoryId, "cityId": cityId}
            except Exception as e:
                print("评分链接格式错误", e)
            print("key", key_dict)
            reviewAndStarUrl = "http://www.dianping.com/ajax/json/shopDynamic/reviewAndStar?"
            html = scrapy(reviewAndStarUrl, "star", key_dict)
            taste, environment, service = html
            info['tastescore'] = eval(taste)
            info['environment'] = eval(environment)
            info['service'] = eval(service)
            # 获取联系方式
            get_data(shop_content, '//*[@id="basic-info"]/p/text()', 'phone')
            # 根据名字由腾讯poi获取经纬度
            try:
                lon, lat = get_location(info['shopname'])
                info['longitude'] = lon
                info['latitude'] = lat
            except Exception as e:
                print("经纬度获取数据错误", e)
                info['longitude'] = 0.0
                info['latitude'] = 0.0
            result.append(info)
            # 限制获得几条数据
            if len(result) > 50:
                return
            time.sleep(random.randint(0, 1) + random.random())
    return shop_name_tem


items_shop = getFoodShop()
file = pd.DataFrame(result)
file.to_excel('./店铺数据.xlsx', index=False)

