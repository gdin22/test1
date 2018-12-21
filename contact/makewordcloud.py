from pymongo import MongoClient
from scipy.misc import imread
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt


class makeWordCloud(object):
    def __init__(self):
        conn = MongoClient('localhost', 27017)
        self.comment = conn.amazon.comment
        self.background = imread('static/image/background.jpg')
        self.background_color = 'white'
        self.max_words = 200,
        self.mask = self.background,
        self.font_path = r'C:/Windows/Fonts/STFANGSO.ttf',
        self.random_state = 42,
        self.prefer_horizontal = 0.9,
        self.scale = 2.0,
        self.min_font_size = 4,
        self.mode = "RGBA",
        self.relative_scaling = 0.5,
        self.collocations = 1,
        self.random_state = 1

    def getAsin(self, asin):  # 获得一个asin的所有颜色列表 尺寸列表 星级列表
        eachAsinComments = self.comment.find({'asin': asin})
        colorlist = [each['color'] for each in eachAsinComments]
        eachAsinComments = self.comment.find({'asin': asin})
        sizelist = [each['size'] for each in eachAsinComments]
        eachAsinComments = self.comment.find({'asin': asin})
        starlist = [each['star'] for each in eachAsinComments]
        colors = list(set(colorlist))
        sizes = list(set(sizelist))
        stars = list(set(starlist))
        print(colors, sizes, stars)
        return colors, sizes, stars

    def output(self):  # 测试用
        print(self.comment.find_one())

    def randomGetText(self, searchState):  # 随机asin中的星级 颜色 和 尺寸
        text = ' '.join([i['comment'] for i in self.comment.find(searchState)])
        print(text)
        return text, searchState

    def getcloud(self, searchState):  # 运行的程序 用来绘制和保存图片 图片的名字为 子asin
        text, searchState = self.randomGetText(searchState)
        wc = self.makecloud()
        wc.generate(text)
        image_colors = ImageColorGenerator(self.background)
        plt.imshow(wc)
        plt.axis('off')
        plt.figure()
        plt.imshow(wc.recolor(color_func=image_colors))
        plt.axis('off')
        asin = searchState['asin']
        color = searchState.get('color', 'call')
        size = searchState.get('size', 'siall')
        star = searchState.get('star', 'stall')
        wc.to_file('static/image/%s_%s_%s_%s.png' % (asin, color, size, star))

    def makecloud(self):
        wc = WordCloud(background_color='white',  # 背景颜色
                       max_words=1000,  # 最大词数
                       mask=self.background,  # 以该参数值作图绘制词云，这个参数不为空时，width和height会被忽略
                       max_font_size=100,  # 显示字体的最大值
                       stopwords=STOPWORDS,  # 使用内置的屏蔽词，再添加'苟利国'
                       font_path="C:/Windows/Fonts/STFANGSO.ttf",  # 解决显示口字型乱码问题，可进入C:/Windows/Fonts/目录更换字体
                       random_state=42,  # 为每个词返回一个PIL颜色
                       # width=1000,  # 图片的宽
                       # height=860,  #图片的长
                       prefer_horizontal=0.9,  # 词语水平方向排版出现的频率 默认0.9
                       scale=3.0,  # 按照比例进行放大画布 如设置为1.5 则长和宽都是原来画布的1.5倍
                       min_font_size=6,  # 显示的最小的字体大小
                       mode="RGBA",  # 当参数为“RGBA”且background_color不为空时，背景为透明
                       relative_scaling=0.5,  # 词频和字体大小的关联性
                       color_func=None,  # 生成新颜色的函数，如果为空，则使用self.color_func
                       regexp=None,  # 使用正则表达式分隔输入的文本
                       collocations=True,  # 是否包括两个词的搭配
                       colormap="viridis",  # 给每个单词随机分配颜色，若指定color_func,则忽略该方法
                       )
        return wc

    def addStopWords(self, *args):  # 添加屏蔽词
        for stopword in args:
            STOPWORDS.add(stopword)
