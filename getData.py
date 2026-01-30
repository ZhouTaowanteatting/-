import os
import pandas as pd
from tools.getDataBase import get_conn
import warnings
warnings.filterwarnings("ignore")

# 获取当前我呢间所在目录的绝对路径
# E:\PycharmProjects\kjdouban\tools
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# E:\PycharmProjects\kjdouban\tools\data
TOOLS_DIR = os.path.join(BASE_DIR, 'data')
# 确保目录存在，不存在则创建
if not os.path.exists(TOOLS_DIR):
    os.mkdir(TOOLS_DIR)


# 数据获取
def dataExport():
    # 获取数据对象
    conn, cursor = get_conn()
    sql = 'select id,directors,rate,title,casts,year,types,country,lang,time,movieTime,commentLen,star from movies'
    # 使用pandas获取数据库中的数据
    data = pd.read_sql(sql, conn)
    if not data.empty:  # 不为空则保存数据
        data.to_csv(os.path.join(TOOLS_DIR, 'moviesData.csv'), index=False, encoding='utf-8')
    else:
        print('查询结果为空，未导出数据！！！')


def mainFun():
    dataExport()

# 统计电影类型TOP6数量
def typesData():
    # 读取数据
    data = pd.read_csv(os.path.join(TOOLS_DIR, 'moviesData.csv'), encoding='utf-8')
    # expand=True扩展为一个数据框，level表示去掉多余的层次，drop=True删除原来的索引,保存为一维数据
    df_split = data['types'].str.split(',', expand=True).stack().reset_index(level=1, drop=True)
    # 统计每个类型的数据
    type_counts = df_split.value_counts()
    # 转为DataFrame
    type_counts_df = type_counts.reset_index()
    # 构建新的标签
    type_counts_df.columns = ['类型', '数量']
    # 获取前5数据
    data01 = type_counts_df.head()
    # 将结果写入CSV文件中
    data01.to_csv(os.path.join(TOOLS_DIR, 'type_counts.csv'), index=False, encoding='utf-8')


# 年份电影数据量的TOP5
def yearData():
    # 读取数据
    data = pd.read_csv(os.path.join(TOOLS_DIR, 'moviesData.csv'), encoding='utf-8')
    # 统计每个年份的数量
    year_counts = data['year'].value_counts()
    # 转为DataFrame
    year_counts_df = year_counts.reset_index()
    # 构建新的标签
    year_counts_df.columns = ['年份', '数量']
    # 读取前5
    data02 = year_counts_df.head()
    # 将结果写入CSV文件中
    data02.to_csv(os.path.join(TOOLS_DIR, 'year_counts.csv'), index=False, encoding='utf-8')


# 统计电影语言前2的数据
def langData():
    # 读取数据
    data = pd.read_csv(os.path.join(TOOLS_DIR, 'moviesData.csv'), encoding='utf-8')
    # expand=True扩展为一个数据框，level表示去掉多余的层次，drop=True删除原来的索引,保存为一维数据
    df_split = data['lang'].str.split(',', expand=True).stack().reset_index(level=1, drop=True)
    # 统计每个语言的数据
    language_counts = df_split.value_counts()
    # 转为DataFrame
    language_counts_df = language_counts.reset_index()
    # 构建新的标签
    language_counts_df.columns = ['语言', '数量']
    # 读取前2
    data03 = language_counts_df.head(2)
    data03.to_csv(os.path.join(TOOLS_DIR, 'lang_counts.csv'), index=False, encoding='utf-8')


# 统计电影评论TOP5数据
def commentsData():
    # 读取数据
    data = pd.read_csv(os.path.join(TOOLS_DIR, 'moviesData.csv'), encoding='utf-8')
    # 将评论数据转为整数型
    data['commentLen'] = data['commentLen'].astype(int)
    # 根据commentLen列对数据进行排序
    top5_comments = data.sort_values(by='commentLen', ascending=False).head()
    # 获取电影名字和评论数据
    top5_comments = top5_comments[['title', 'commentLen']]
    top5_comments.columns = ['电影', '数量']
    top5_comments.to_csv(os.path.join(TOOLS_DIR, 'comment_counts.csv'), index=False, encoding='utf-8')


# 统计不同获奖电影数据量（前10）
def countyData():
    # 读取数据
    data = pd.read_csv(os.path.join(TOOLS_DIR, 'moviesData.csv'), encoding='utf-8')
    # expand=True扩展为一个数据框，level表示去掉多余的层次，drop=True删除原来的索引,保存为一维数据
    df_split = data['country'].str.split(',', expand=True).stack().reset_index(level=1, drop=True)
    county_counts = df_split.value_counts()
    county_counts_df = county_counts.reset_index()
    county_counts_df.columns = ['国家', '数量']
    data05 = county_counts_df.head(10)
    data05.to_csv(os.path.join(TOOLS_DIR, 'country_counts.csv'), index=False, encoding='utf-8')


def mainFun():
    dataExport()
    typesData()
    yearData()
    langData()
    commentsData()
    countyData()


if __name__ == '__main__':
    mainFun()


if __name__ == '__main__':
    mainFun()