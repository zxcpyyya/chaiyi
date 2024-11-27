import pandas as pd
import requests
import time
import random
from lxml import etree
import urllib3

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 设置文件路径
input_file_path = r"C:\Users\Administrator\Desktop\菜\湘菜.xlsx"
output_file_path = r"C:\Users\Administrator\Desktop\菜\test.xlsx"

# 读取 Excel 文件的第一列数据，从第二行开始
df = pd.read_excel(input_file_path, usecols=[0], header=None)
data = df.iloc[1:].reset_index(drop=True)

# 存储输出数据
output_data = []

# 获取营业时间的函数
def get_time():
    for index, value in data.iterrows():
        shop_id = value[0]  # 当前行的商店 ID
        print(f"正在处理商店 {index + 1}: {shop_id}")

        # 构造 URL 和请求头
        url = f"http://www.dianping.com/shopold/pc?shopuuid={shop_id}"
        headers = {
            "cookie":"_lxsdk_cuid=19237fabf66c8-071fef50227867-26001051-1bcab9-19237fabf66c8; _lxsdk=19237fabf66c8-071fef50227867-26001051-1bcab9-19237fabf66c8; _hc.v=3ad3b14e-d95e-3f51-285e-d888e5fcce87.1727516033; WEBDFPID=y75v84y6ywu552y0yu8u452x63x56v3980762uzuuv797958541zw727-2042876037302-1727516036816EKOESCKfd79fef3d01d5e9aadc18ccd4d0c95077509; ctu=5483ce84c2909393248edc3325ed53c8655fa979e2548b0c071fa8ff3478e00c; s_ViewType=10; cy=5; cye=nanjing; aburl=1; cityid=5; default_ab=shopList%3AA%3A5; ua=%E6%88%91%E4%B8%8D%E7%9F%A5%E9%81%93; fspop=test; qruuid=c63464ae-0f93-4146-807f-bc430e79ea3b; dplet=db46c0231ec5ce5844e58bb61d42c1c4; dper=02026722e2075b42bb5be85d50d0c6b1077051794524e9f58290fefc1cb61d2385cf677f1f9527c5fd3226034e28a9420cfecbcade0c98ef96dc00000000982400003d8c1ed95184f763f7a2a3122341966f4eb8d3fa9f53bec1d21f1e170c9e4665fdbb96653d84b1f601927c90311e6ea7; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1731593878,1731859035,1731925073,1732025190; ll=7fd06e815b796be3df069dec7836c3df",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }

        try:
            # 发送 GET 请求
            response = requests.get(url=url, headers=headers, timeout=15, verify=False)
            response.encoding = "utf-8"

            # 解析 HTML 内容
            tree = etree.HTML(response.text)

            # 使用 XPath 提取营业时间
            time_elements = tree.xpath('//*[@id="basic-info"]/div[4]/p[1]/span[2]/text()')
            time1 = time_elements[0].strip("()") if time_elements else "暂无"

            print("营业时间:", time1)

            # 将商店 ID 和营业时间存入列表
            output_data.append([shop_id, time1])

        except requests.exceptions.RequestException as req_err:
            print(f"请求商店 {shop_id} 时出错: {req_err}")
            output_data.append([shop_id, "请求错误"])
        except etree.XPathError as xpath_err:
            print(f"解析商店 {shop_id} 时出错: {xpath_err}")
            output_data.append([shop_id, "解析错误"])
        except Exception as e:
            print(f"未知错误: 商店 {shop_id}, 错误信息: {e}")
            output_data.append([shop_id, "未知错误"])
        finally:
            # 添加动态间隔
            sleep_time = random.uniform(5, 10)
            print(f"等待 {sleep_time:.2f} 秒...")
            time.sleep(sleep_time)

# 主程序入口
if __name__ == '__main__':
    get_time()
    output_df = pd.DataFrame(output_data, columns=["商店ID", "营业时间"])  # 添加表头
    output_df.to_excel(output_file_path, index=False)  # 不写入索引
    print("数据已成功写入:", output_file_path)
