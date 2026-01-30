from tools.actor import *
from tools.addressData import *
from tools.homeData import *
from tools.rateData import *
from tools.timeData import *
from tools.typeData import *
from tools.getDataBase import get_conn
from flask import Flask, render_template, request
from flask import redirect, url_for, session
from tools.word_cloud import *
from tools.getData import mainFun
from functools import wraps



# 创建Flask的对象，指定静态文件和模板文件
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'ywqq'

#实现4040
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # 如果没有登录，则重定向到登录界面
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function

# 实现一个视图函数，作为根路由
@app.route('/')
def rootRoute():
    return render_template('login.html')



# 实现注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']  # 获取用户名和密码
        password = request.form['password']
        if not username or not password:
            # 如果没有用户和密码，则重定向回注册视图界面
            return redirect(url_for('register'))
        # 判断两次输入的密码是否一致
        if request.form['password'] != request.form['passwordCheked']:
            return '<h1>两次密码不一致！！！</h1>'
        # 获取数据的
        conn, cursor = get_conn()
        cursor.execute('select username from users')
        data = cursor.fetchall()  # 查看数据库中所有的用户信息
        userList = [user[0] for user in data]
        if username in userList:
            return '<h1>用户名已经存在！！！</h1>'
        # 如果填写的信息完全正确，就将信息写入到数据库黄总工
        cursor.execute('insert into users (username, password) values (%s, %s)', (username, password))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# 实现登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取用户名和密码
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            # 如果没有用户和密码，则重定向回注册视图界面
            return redirect(url_for('login'))
        conn, cursor = get_conn()
        cursor.execute('select * from users where username="%s" and password="%s"' % (username, password))
        user = cursor.fetchone()  # 找到一个即可
        if user:  # 如果存在用户名，则保存用户名到session中，并且跳转到home界面
            session['username'] = username
            return redirect(url_for('home'))
        else:  # 如果没有用户名则跳转回登录界面
            return redirect(url_for('login'))
    return render_template('login.html')
# 实现首页
@app.route('/home')
def home():
    username = session['username']
    # 获取首页需要显示的所有信息，并从后台--前端进行展示出来
    allData = getAllData()  # 获取所有的电影数据
    dataLen = len(allData)  # 统计长度
    maxRate = getMaxRate()  # 电影的最高分数
    maxCast = getMaxCast()  # 电影的出场最多的演员
    typeAll = getTypesAll()  # 获取电影种类数据
    typeAll = len(typeAll)  # 统计长度
    maxLang = getMaxLang()  # 获取最多的语言
    # 获取图表需要的数据
    types = getType_t()  # 电影种类饼状图的数据
    x, y = getRate_t()  # 电影评分折线图数据
    return render_template('home.html', username=username,
                           dataLen=dataLen, maxRate=maxRate,
                           maxCast=maxCast, typeAll=typeAll,
                           maxLang=maxLang, types=types,
                           x=list(x), y=list(y))

# 实现搜索
@app.route('/search/<int:serachId>', methods=['GET', 'POST'])
def search(serachId):
    username = session['username']
    allData = getAllData()  # 获取所有的电影数据
    data = []  # 初始化列表，用户存储过滤的数据
    if request.method == 'GET':
        if serachId == 0:
            return render_template('search.html', username=username, data=data)
        # 遍历所有的电影，找到跟你点击的电影ID一致的电影
        for i in allData:
            if i[0] == serachId:
                data.append(i)
        return render_template('search.html', username=username, data=data)
    else:  # POST
        searchWord = request.form['searchIpt']
        if not searchWord:  # 如果搜索框为空，则重定向回该界面
            return redirect(url_for('search',serachId=serachId))

        # 如果有数据，则进行过滤操作，定一个过滤函数，用于过滤数据
        def filterFun(item):
            if item[3].find(searchWord) == -1:
                return False
            else:
                return True

        data = list(filter(filterFun, allData))
        return render_template('search.html', username=username, data=data)

# 实现时间分析表
@app.route('/time_t')
def time_t():
    username = session['username']
    x, y = getTimeList()  # 历年产量统计
    movieTimeData = getMovieTimeList()  # 电影时长分布占比
    return render_template('time_t.html', username=username,
                           x=list(x), y=list(y), movieTimeData=movieTimeData)
# 实现评分分析表
@app.route('/rate_t/<type>', methods=['GET', 'POST'])
def rate_t(type):
    username = session['username']
    # 电影评分统计
    typeAll = getTypesAll()  # 获取电影种类
    if type == 'all':
        x, y = getRate_t()  # 获取所有的电影种类的评分
    else:
        x, y = getRate_tType(type)  # 获取不同类型的电影评分
    # 豆瓣评分星级饼状图
    if request.method == 'GET':
        star, movieName = getStart("")  # 不写则绘制数据库中第一条电影的数据
    else:
        searchWord = request.form['searchIpt'].strip()
        # 如果没有问题就获取输入电源的星级占比和名称
        try:
            star, movieName = getStart(searchWord)
        except Exception as e:
            return redirect(url_for('rate_t', type=type))
    # 豆瓣年度评价评分柱状图的数据
    x1, y1 = getMean()
    # 豆瓣电影中外评分分布图
    x2, y2, y22 = getCountryRating()
    return render_template('rate_t.html', username=username,
                           x=list(x), y=list(y), star=star, movieName=movieName,
                           x1=x1, y1=y1, x2=x2, y2=y2, y22=y22,typeAll=typeAll)

# 实现地图分析表
@app.route('/address_t')
def address_t():
    username = session['username']
    x, y = getAddressData()  # 电影拍摄地点统计图
    x1, y1 = getLangData()  # 电影语言统计图
    return render_template('address_t.html', username=username,
                           x=x, y=y, x1=x1, y1=y1)
# 实现类型分析表
@app.route('/type_t')
@login_required
def type_t():
    username = session['username']
    result = getMovieTypeData()
    data = sorted(result, key=lambda x: x['value'], reverse=True)
    top5Data = data[:8]
    return render_template('type_t.html', username=username, top5Data=top5Data)
# 实现导演和演员分析表
@app.route('/actor_t')
@login_required
def actor_t():
    username = session['username']
    x, y = getAllActorMovieNum()  # 导演前20
    x1, y1 = getAllDirectorMovieNum()  # 演员前20
    return render_template('actor_t.html', username=username, x=x, y=y, x1=x1, y1=y1)
#数据列表
@app.route('/tables/<int:id>')
def tables(id):
    username = session['username']
    tablelist=[]
    if id == 0:
        tablelist=getTableList()
    return render_template('tables.html', username=username, tablelist=tablelist)


# 实现标题词云
@app.route('/title_c')
def title_c():
    username = session['username']
    # 调用词云文件中的函数，进行绘制词云
    getTitleImg('title', 'fas fa-dog', './static/images/title.png')
    return render_template('title_c.html', username=username)
# 实现演员名词云
@app.route('/casts_c')
def casts_c():
    username = session['username']
    # 调用词云文件中的函数，进行绘制词云
    getCastsImg('casts', 'fas fa-sun', './static/images/casts.png')
    return render_template('casts_c.html', username=username)

# 实现自定义词云图
@app.route('/comments_c', methods=['GET', 'POST'])
def comments_c():
    username = session['username']
    if request.method == 'GET':  # 不做任何操作
        return render_template('comments_c.html', username=username)
    else:  # POST请求
        searchWord = request.form['searchIpt']
        try:
            getCommentsImg('commentContent', searchWord, 'fab fa-qq', './static/images/comments.png')
        except Exception as e:
            return redirect(url_for('comments_c'))
    return render_template('comments_c.html', username=username)


#实现大屏可视化界面
@app.route('/analysis1', methods=['GET', 'POST'])
def index():
    # 获取首页需要显示的所有信息，并从后台--前端进行展示出来
    allData = getAllData()  # 获取所有的电影数据
    allData = len(allData)  # 统计长度
    maxRate = getMaxRate()  # 电影的最高分数
    typeAll = getTypesAll()  # 获取电影种类数据
    typeAll = len(typeAll)  # 统计长度
    maxLang = getMaxLang()[:2]  # 获取最多的语言
    data={
        'allData':allData,
        'maxRate':maxRate,
        'typeAll':typeAll,
        'maxLang':maxLang
    }
    #调用大屏可视化函数
    chart_html1 = typeData()
    chart_html2 = yearData()
    chart_html3 = langData()
    chart_html4= commentData()
    worldData()
    return render_template('analysis.html', data=data, chart_html1=chart_html1, chart_html2=chart_html2,chart_html3=chart_html3,chart_html4=chart_html4)


import pandas as pd
from pyecharts.charts import *  # 导入所有的图表
from pyecharts import options as opts  # 导入配置项

# 电影类型TOP5
def typeData():
    # 读取数据
    data = pd.read_csv('./tools/data/type_counts.csv', encoding='utf-8')
    # [('剧情', 113), ('喜剧', 47), ('冒险', 41), ('奇幻', 38), ('爱情', 34)]
    pie_data = list(zip(data['类型'], data['数量']))
    print(pie_data)
    pie = Pie(init_opts=opts.InitOpts(height='400px', width='500px'))
    pie.add('数量',
            pie_data,
            radius=['30%', '60%'],
            label_opts=opts.LabelOpts(formatter="{b}:{c}个", font_size=16, font_style='bold', color='#0f0'))
    # 设置配置项
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title=''),
        legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(font_size=16, color='#0f0'))
    )
    # 产生一个HTML文件
    pie.render('static/html/type_data.html')
    chart_html1 = pie.render_embed()
    return chart_html1

# 统计年份电影TOP5数量
def yearData():
    # 读取数据
    data = pd.read_csv('./tools/data/year_counts.csv', encoding='utf-8')
    years = data['年份'].tolist()
    counts = data['数量'].tolist()
    bar = Bar(init_opts=opts.InitOpts(height='400px', width='500px'))
    bar.add_xaxis(years)
    bar.add_yaxis('数量', counts)
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title=''),
        xaxis_opts=opts.AxisOpts(name='年份',
                                 name_textstyle_opts=opts.TextStyleOpts(color='#0f0'),
                                 axislabel_opts=opts.LabelOpts(font_size=12, color='#0f0')),
        yaxis_opts=opts.AxisOpts(name='数量',
                                 name_textstyle_opts=opts.TextStyleOpts(color='#0f0'),
                                 axislabel_opts=opts.LabelOpts(font_size=12, color='#0f0')),
        legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='#0f0', font_size=12)),
        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross')
    )
    bar.set_series_opts(itemstyle_opts=opts.ItemStyleOpts('#0ff'))

    bar.render('static/html/year_data.html')
    chart_html2 = bar.render_embed()
    return chart_html2

# 中英文电影占比
def langData():
    data = pd.read_csv('./tools/data/lang_counts.csv', encoding='utf-8')
    # [['汉语普通话', 92], ['英语', 83]]
    result = [[row['语言'], row['数量']] for index, row in data.iterrows()]
    # 计算中英文的总数，用于计算百分比
    sum_value = result[0][1] + result[1][1]
    # 中文水球图
    li1 = Liquid(init_opts=opts.InitOpts(height='100px', width='100px'))
    li1.add(
        '占比',
        [result[0][1] / sum_value],
        center=['15%', '35%'],
        color=['#0f0'],
        is_outline_show=False,
        shape='pin',
        label_opts=opts.LabelOpts(font_size=40),
    )
    li1.set_global_opts(title_opts=opts.TitleOpts(title=result[0][0][:2], pos_left='13%',
                                                  pos_top='3%',
                                                  title_textstyle_opts=opts.TextStyleOpts(color='#0f0')))

    # 英文水球图
    li2 = Liquid(init_opts=opts.InitOpts(height='100px', width='100px'))
    li2.add(
        '占比',
        [result[1][1] / sum_value],
        center=['35%', '35%'],
        is_outline_show=False,
        shape='pin',
        label_opts=opts.LabelOpts(font_size=40))
    li2.set_global_opts(title_opts=opts.TitleOpts(title=result[1][0][:2], pos_left='32%',
                                                  pos_top='3%',
                                                  title_textstyle_opts=opts.TextStyleOpts(color='#0f0')))
    # 组合
    grid = Grid()
    grid.add(li1, grid_opts=opts.GridOpts())
    grid.add(li2, grid_opts=opts.GridOpts())
    grid.render('static/html/lang_data.html')
    chart_html3 = grid.render_embed()
    return chart_html3

# 电影评论数柱状图
def commentData():
    data = pd.read_csv('./tools/data/comment_counts.csv', encoding='utf-8')
    names = data['电影'].tolist()
    counts = data['数量'].tolist()
    bar = Bar(init_opts=opts.InitOpts(height='400px', width='500px'))
    bar.add_xaxis(names)
    bar.add_yaxis('评论数量', counts)
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title=''),
        xaxis_opts=opts.AxisOpts(name='电影',
                                 name_textstyle_opts=opts.TextStyleOpts(color='#0f0'),
                                 axislabel_opts=opts.LabelOpts(font_size=12,rotate=45, color='#0f0')),
        yaxis_opts=opts.AxisOpts(name='数量',
                                 min_=50000,
                                 max_=3500000,
                                 name_textstyle_opts=opts.TextStyleOpts(color='#0f0'),
                                 axislabel_opts=opts.LabelOpts(font_size=10,rotate=45, color='#0f0')),
        legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='#0f0', font_size=12)),
        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross')
    )
    bar.set_series_opts(itemstyle_opts=opts.ItemStyleOpts('#ccff66'))

    bar.render('static/html/comment_data.html')
    chart_html4 = bar.render_embed()
    return chart_html4

# 地球
def worldData():
    data = pd.read_csv('./tools/data/country_counts.csv', encoding='utf-8')
    # [['中国大陆', 87], ['美国', 65], ['中国香港', 21], ['英国', 20], ['日本', 12],
    # ['法国', 10], ['加拿大', 5], ['意大利', 5], ['中国台湾', 4], ['德国', 4]]
    data_list = data.values.tolist()
    # 提供国家地区数据，用于替换原数据中国家的名称（只是为了替换一些面积大一些的国家，在地图上好看一些）
    country_name = ['Russia', 'Canada', 'China', 'USA', 'Brazil', 'Australia', 'India', 'Argentina', 'France',
                    'Germany']
    replace_data = []
    # [['Russia', 87], ['Canada', 65], ['China', 21], ['USA', 20], ['Brazil', 12], ['Australia', 10],
    # ['India', 5], ['Argentina', 5], ['France', 4], ['Germany', 4]]
    for i in range(len(country_name)):
        replace_data.append([country_name[i], data_list[i][1]])

    map = MapGlobe(init_opts=opts.InitOpts(height='500px', width='450px'))
    map.add(maptype='world', series_name='数量', data_pair=replace_data)
    map.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            min_=4,
            max_=87,
            type_='color',
            range_color=['#f00', '#00f']
        )
    )
    map.render('static/html/map3d.html')
#实现退出
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

from functools import wraps


if __name__ == '__main__':
    with app.app_context():
        mainFun()
    app.run(debug=True, port=9898)