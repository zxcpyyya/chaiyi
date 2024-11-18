import pandas as pd
import mysql.connector
from config import Config
import os

def get_district_and_id_from_coordinates(lat, lng):
    """根据经纬度判断位于南京哪个区并返回对应的区ID"""
    # 南京各区域经纬度范围
    district_bounds = {
        "玄武区": {"lat": (32.02, 32.17), "lng": (118.77, 118.93), "id": 1},
        "秦淮区": {"lat": (31.95, 32.04), "lng": (118.75, 118.85), "id": 2},
        "建邺区": {"lat": (31.88, 32.04), "lng": (118.64, 118.77), "id": 3},
        "鼓楼区": {"lat": (32.02, 32.12), "lng": (118.71, 118.80), "id": 4},
        "浦口区": {"lat": (31.95, 32.40), "lng": (118.50, 118.75), "id": 5},
        "栖霞区": {"lat": (31.85, 32.20), "lng": (118.80, 119.20), "id": 6},
        "雨花台区": {"lat": (31.85, 32.00), "lng": (118.72, 118.85), "id": 7},
        "江宁区": {"lat": (31.70, 32.00), "lng": (118.75, 119.10), "id": 8},
        "六合区": {"lat": (32.15, 32.50), "lng": (118.65, 119.00), "id": 9},
        "溧水区": {"lat": (31.55, 31.80), "lng": (118.85, 119.20), "id": 10},
        "高淳区": {"lat": (31.25, 31.60), "lng": (118.75, 119.15), "id": 11}
    }
    
    for district, bounds in district_bounds.items():
        if (bounds["lat"][0] <= lat <= bounds["lat"][1] and 
            bounds["lng"][0] <= lng <= bounds["lng"][1]):
            return district, bounds["id"]
    return "未知区域", None

def process_locations_and_update_ids():
    try:
        # 获取dishes目录下所有xlsx文件
        dishes_dir = 'dishes'
        excel_files = [f for f in os.listdir(dishes_dir) if f.endswith('.xlsx')]
        
        for excel_file in excel_files:
            file_path = os.path.join(dishes_dir, excel_file)
            print(f"\n处理文件: {excel_file}")
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 确保经纬度列存在
            if 'latitude' not in df.columns or 'longitude' not in df.columns:
                print(f"警告: {excel_file} 中没有找到经纬度列，跳过此文件")
                continue
            
            # 根据经纬度范围判断所属区域和区ID
            districts_and_ids = df.apply(lambda row: get_district_and_id_from_coordinates(row['latitude'], row['longitude']), axis=1)
            df['region'] = districts_and_ids.apply(lambda x: x[0])
            df['region_id'] = districts_and_ids.apply(lambda x: x[1])
            
            # 保存结果
            df.to_excel(file_path, index=False)
            print(f"处理完成，结果已保存到 {file_path}")
            
            # 统计各区商家数量
            district_stats = df['region'].value_counts()
            print(f"\n{excel_file} 各区商家数量统计:")
            print(district_stats)
            
            # 统计未知区域的经纬度
            unknown_locations = df[df['region'] == '未知区域'][['latitude', 'longitude']].values.tolist()
            if unknown_locations:
                print(f"\n{excel_file} 中未能识别区域的经纬度:")
                for lat, lng in unknown_locations:
                    print(f"纬度:{lat}, 经度:{lng}")
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")

if __name__ == "__main__":
    process_locations_and_update_ids()
