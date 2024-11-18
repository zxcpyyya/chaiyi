import mysql.connector
from mysql.connector import Error

def insert_categories():
    try:
        # 连接数据库
        conn = mysql.connector.connect(
            host="localhost",
            user="root", 
            password="ldf052821",
            database="xiaodachuang",
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor()

        # 要插入的菜系列表
        categories = [
            "川菜",
            "北京菜", 
            "东北菜",
            "新疆菜",
            "粤菜",
            "鲁菜",
            "黔菜",
            "江浙菜"
        ]

        # 插入数据
        for category in categories:
            try:
                cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category,))
                print(f"成功插入菜系: {category}")
            except Error as e:
                print(f"插入 {category} 时出错: {e}")
                continue

        # 提交事务
        conn.commit()

    except Error as e:
        print(f"数据库连接错误: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    insert_categories()
