import pandas as pd
import requests
import time
from lxml import etree
import re
import random

# 设置文件路径
input_file_path = r"C:\Users\Administrator\Desktop\菜\输入文件.xlsx"
output_file_path = r"C:\Users\Administrator\Desktop\菜\输出文件.xlsx"  # 新文件的路径

# 读取 Excel 文件的第一列数据，从第二行开始
df = pd.read_excel(input_file_path, usecols=[0], header=None)
data = df.iloc[1:].reset_index(drop=True)

# 遍历并输出每个字符串，并将其存储在一个列表中
output_data = []  # 创建一个列表来存储输出数据


def clean_phone_number(phone):
    if not phone:
        return "暂无电话"

    # 1. 去掉 "电话:" 前缀
    phone = phone.replace("电话:", "").strip()

    # 2. 使用正则表达式去掉重复区号，例如 "025-025-" 变成 "025-"
    phone = re.sub(r'\b(\d{3})-\1-', r'\1-', phone)

    return phone


def get_iphone_remark():
    for index, value in data.iterrows():
        print(f"正在处理商店 {index}: {value[0]}")
        shop_id = value[0]  # 获取当前行的字符串（商店ID）

        # 构造 URL
        url = f"http://www.dianping.com/shop/{shop_id}/review_all?queryType=isAll&queryVal=true"
        headers = {

    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9",
    "connection": "keep-alive",
    "cookie": "_lxsdk_cuid=19237fabf66c8-071fef50227867-26001051-1bcab9-19237fabf66c8; _lxsdk=19237fabf66c8-071fef50227867-26001051-1bcab9-19237fabf66c8; _hc.v=3ad3b14e-d95e-3f51-285e-d888e5fcce87.1727516033; WEBDFPID=y75v84y6ywu552y0yu8u452x63x56v3980762uzuuv797958541zw727-2042876037302-1727516036816EKOESCKfd79fef3d01d5e9aadc18ccd4d0c95077509; ctu=5483ce84c2909393248edc3325ed53c8655fa979e2548b0c071fa8ff3478e00c; s_ViewType=10; cy=5; cye=nanjing; aburl=1; cityid=5; default_ab=shopList%3AA%3A5; ua=%E6%88%91%E4%B8%8D%E7%9F%A5%E9%81%93; fspop=test; qruuid=c63464ae-0f93-4146-807f-bc430e79ea3b; dplet=db46c0231ec5ce5844e58bb61d42c1c4; dper=02026722e2075b42bb5be85d50d0c6b1077051794524e9f58290fefc1cb61d2385cf677f1f9527c5fd3226034e28a9420cfecbcade0c98ef96dc00000000982400003d8c1ed95184f763f7a2a3122341966f4eb8d3fa9f53bec1d21f1e170c9e4665fdbb96653d84b1f601927c90311e6ea7; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1731593878,1731859035,1731925073,1732025190; ll=7fd06e815b796be3df069dec7836c3df",
    "host": "www.dianping.com",
    "referer": "https://www.dianping.com/shop/G89nErZQNNnn5OUK/review_all?queryType=isPic&queryVal=true",
    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}




        try:
            response = requests.get(url=url, headers=headers, timeout=15, verify=False)
            response.encoding = "utf-8"
            content = response.text

            # 提取数据（例如评论、联系方式等）
            tree = etree.HTML(content)


            # 提取并清理评论数量（好评、中评、差评）
            remarks_good = tree.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[2]/div[1]/label[3]/span/text()')
            remarks_good = remarks_good[0].strip("()") if remarks_good else "暂无"

            remarks_neutral = tree.xpath(
                '//*[@id="review-list"]/div[2]/div[3]/div[3]/div[2]/div[1]/label[4]/span/text()')
            remarks_neutral = remarks_neutral[0].strip("()") if remarks_neutral else "暂无"

            remarks_bad = tree.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[2]/div[1]/label[5]/span/text()')
            remarks_bad = remarks_bad[0].strip("()") if remarks_bad else "暂无"


            print("好评数量:", remarks_good)
            print("中评数量:", remarks_neutral)
            print("差评数量:", remarks_bad)

            # 将数据添加到输出列表
            output_data.append([shop_id,  remarks_good, remarks_neutral, remarks_bad])

        except Exception as e:
            print(f"获取商店 {shop_id} 时出错: {e}")
            output_data.append([shop_id, "出错", "出错", "出错", "出错"])

            # 添加适当的休眠时间，避免频繁请求
        sleep_time = random.uniform(5, 10)
        print(f"等待 {sleep_time:.2f} 秒...")
        time.sleep(sleep_time)


# 将输出数据写入新的 Excel 文件
if __name__ == '__main__':
    get_iphone_remark()
    output_df = pd.DataFrame(output_data, columns=["商店ID", "好评", "中评", "差评"])  # 添加表头
    output_df.to_excel(output_file_path, index=False)  # 不写入索引
    print("数据已成功写入:", output_file_path)