import pymysql

# 连接数据库
def get_conn():
    # 主机、用户名、密码、数据库名称、端口号
    conn = pymysql.connect(host='localhost', user='root', password='123456', database='movie_spider', port=3306)
    cursor = conn.cursor()
    return conn, cursor