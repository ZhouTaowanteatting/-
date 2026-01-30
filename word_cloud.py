import stylecloud
from tools.getDataBase import get_conn

# 实现绘制标题词云
# 需要绘制的字段、图标名称、输出名称
def getTitleImg(field, icon_name, output_name):
    sql = f'select {field} from movies'
    conn, cursor = get_conn()
    cursor.execute(sql)
    data = cursor.fetchall()  # 获取所有的查询结果
    text1 = ','.join([row[0] for row in data])
    # text1 = ','.join(text1) 这个操作是将标题拆分为一个一个的字
    stylecloud.gen_stylecloud(text=text1,
                              icon_name=icon_name,
                              output_name=output_name,
                              font_path='/static/fonts/simhei.ttf')

# 实现绘制演员名词云
# 需要绘制的字段、图标名称、输出名称
def getCastsImg(field, icon_name, output_name):
    sql = f'select {field} from movies'
    conn, cursor = get_conn()
    cursor.execute(sql)
    data = cursor.fetchall()  # 获取所有的查询结果
    text1 = ','.join([row[0] for row in data])
    # text1 = ','.join(text1) 这个操作是将标题拆分为一个一个的字
    stylecloud.gen_stylecloud(text=text1,
                              icon_name=icon_name,
                              output_name=output_name,
                              font_path='/static/fonts/simhei.ttf')

# 需要绘制的字段、输入的内容、图标名称、输出名称
def getCommentsImg(field, serchWord, icon_name, output_name):
    sql = f'select {field} from comments where movieName="{serchWord}"'
    conn, cursor = get_conn()
    cursor.execute(sql)
    data = cursor.fetchall()  # 获取所有的查询结果
    text1 = ','.join([row[0] for row in data])
    text1 = ','.join(text1) #这个操作是将标题拆分为一个一个的字
    stylecloud.gen_stylecloud(text=text1,
                              icon_name=icon_name,
                              output_name=output_name,
                              font_path='/static/fonts/simhei.ttf')
