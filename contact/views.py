from django.shortcuts import render, HttpResponse, redirect
from contact.models import Contacts, SaveKeys
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.http import HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import time
import xlwt
import xlrd
from pymongo import MongoClient
conn = MongoClient('localhost', 27017)
from contact.makewordcloud import makeWordCloud


# 初始界面， 根据不同的选项跳转到不同的页面
# 如果post则跳转到本页面 对excel进行分析 然后进行截图 重定向到展示页面
# 在开始的时候删除数据库 这是单人用的 如果多人用 可能出现错误
def index(request):
    if request.method == 'POST':
        try:
            excel = request.FILES.get('excel')
            excelPath = os.path.join('static', excel.name)
            print(excelPath)
            f = open(excelPath, 'wb')
            for chunk in excel.chunks(chunk_size=1024):
                f.write(chunk)
            Contacts.objects.all().delete()
            SaveKeys.objects.all().delete()
        except Exception as e:
            error = e
        finally:
            f.close()
            allUrls, keylists = getExcelMessage(excelPath)
            for key in keylists:
                Contacts.objects.create(key=key)
            screenshot(allUrls)
            return redirect('/showPage')
    return render(request, 'index.html')


# 对数据库的内容进行分页 对截取的图片进行分页
def showPage(request):
    contact_list = Contacts.objects.all()
    paginator = Paginator(contact_list, 2)

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    return render(request, 'showPage.html', {'contacts': contacts})


# 分析上传的excel
# 生成链接列表还有关键词列表
def getExcelMessage(fileName):
    workbook = xlrd.open_workbook(fileName)
    sheet = workbook.sheet_by_index(0)
    col0 = sheet.col_values(0)
    urls = []
    for key in col0:
        urls.append('https://www.amazon.com/s/ref=sr_pg_2?page=%s&keywords=%s' % ('1', key))
        urls.append('https://www.amazon.com/s/ref=sr_pg_2?page=%s&keywords=%s' % ('2', key))
    return urls, col0


# 进行截图 但是在apache 上面出现错误 研究
def screenshot(urls):
    for url in urls:
        os.system(r'python contact/screenShot.py "%s"' % url)


# 在展示页面中如果要保存进行提交
# 保存到数据库 不要的进行去除
# 进而保存到excel 重定向到下载页面
def saveExcel(request):
    currenttime = time.time()
    keylist = [contact.key for contact in Contacts.objects.all()]
    if request.method == 'POST':
        if request.POST.get('sub') == '提交':
            for key in keylist:
                if request.POST.get(key) == '1':
                    SaveKeys.objects.create(key=key)
                else:
                    try:
                        SaveKeys.objects.filter(key=key).delete()
                    except:
                        pass
            print('提交')
        else:
            keys = list(set([each.key for each in SaveKeys.objects.all()]))
            saveExcelName = ''.join(['static/', str(int(currenttime)), '.xls'])
            writeExcel(keys, saveExcelName)
            print(saveExcelName)
            return HttpResponseRedirect('/getExcel/%s' % saveExcelName.split('/')[-1])
        page = request.POST.get('page')
        print(page)
    return redirect('/showPage?page=%s' % str(int(page)+1))


# 把列表写进excel
# 参数为 列表 还有 excel名称
def writeExcel(list, excelName):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = "Times New Roman"
    font.bold = False
    font.colour_index = 4
    font.height = 220
    style.font = font

    wd = xlwt.Workbook()
    sheet = wd.add_sheet('0')
    for key in range(0, len(list)):
        sheet.write(key, 0, list[key])

    wd.save(excelName)


# 把 两个列表写入excel
# xlwt 只能写xls
def write2x2Excel(list1, list2, excelName):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = "Times New Roman"
    font.bold = False
    font.colour_index = 4
    font.height = 220
    style.font = font

    wd = xlwt.Workbook()
    sheet = wd.add_sheet('0')
    for key in range(0, len(list1)):
        sheet.write(key, 0, list1[key])
        sheet.write(key, 1, list2[key])
    wd.save(excelName)


# 下载excel表格 一般被用来当做重定向的对象
@csrf_exempt
def getExcel(request, path_name):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    ret = {}
    #file_name = os.path.join('static', path_name)
    file_name = path_name
    if os.path.exists(file_name):
        response = StreamingHttpResponse(file_iterator(file_name))
        response['Content-type'] = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment;filename="%s"' % path_name
        return response
    else:
        ret['result'] = False
        ret['code'] = 200
        ret['message'] = '返回失败'
        return JsonResponse(ret, status=200)


# 把excel中的小写字母转换为大写
# 并加入展示页面的链接
def tranexcel(request):
    if request.method == 'POST':
        try:
            excel = request.FILES.get('excel')
            excelPath = excel.name
            print(excelPath)
            f = open(excelPath, 'wb')
            for chunk in excel.chunks(chunk_size=1024):
                f.write(chunk)
        except Exception as e:
            error = e
        finally:
            f.close()

            allUrls, keylists = getExcelMessage(excelPath)
            keylists = [i.upper() for i in keylists]
            allUrls = ['www.amazon.com/dp/%s' % key for key in keylists]
            excelPath = excelPath[:-1]
            write2x2Excel(keylists, allUrls, excelPath)
            return HttpResponseRedirect('/getExcel/%s' % excelPath)


@csrf_exempt
def get_cloud(request):
    if request.method == 'POST':
        asinDict = conn.amazon.asin.find_one()['asinToSku']
        asinList = list(asinDict)
        comment = conn.amazon.comment
        q = request.POST['q']
        if q not in asinList:
            rejson = []
            for asin in asinList:
                rejson.append(inThisAsin(q, asin))
            return HttpResponse(json.dumps(rejson), content_type='application/json')
        else:
            print(q)
            masin = asinDict[q]
            print(masin)
            colors = [com['color'] for com in comment.find({'asin': masin})]
            colors = list(set(colors))
            sizes = [com['size'] for com in comment.find({'asin': masin})]
            sizes = list(set(sizes))
            stars = [com['star'] for com in comment.find({'asin': masin})]
            stars = list(set(stars))
            try:
                colors.remove('')
            except:
                pass
            try:
                sizes.remove('')
            except:
                pass
            try:
                stars.remove('')
            except:
                pass
            alllist = ['real']
            colorhtml = gen_html(colors)
            alllist.append(colorhtml)
            sizehtml = gen_html(sizes)
            alllist.append(sizehtml)
            starhtml = gen_html(stars)
            alllist.append(starhtml)
            print(alllist)
            return HttpResponse(json.dumps(alllist), content_type='application/json')
    return render(request, 'cloud.html')


def inThisAsin(word, asin):
    if word in asin:
        return asin
    else:
        return '0'


# 这个函数生成select 代码
def gen_html(list):
    html = []
    for i in list:
        html.append('<option value = "%s"> %s </ option>' % (i, i))
    html = ' '.join(html)
    return html


@csrf_exempt
def make_image(request):
    searchDict = {}
    if request.method == 'POST':
        asinDict = conn.amazon.asin.find_one()['asinToSku']
        asin = request.POST['asin']
        masin = asinDict[asin]
        color = request.POST['color']
        size = request.POST['size']
        star = request.POST['star']
        print(request.POST)
        searchDict['asin'] = masin
        if color != 'all':
            searchDict['color'] = color
        if size != 'all':
            searchDict['size'] = size
        if star != 'all':
            searchDict['star'] = float(star)

        print(searchDict)
        make = makeWordCloud()
        make.getcloud(searchDict)

        color = searchDict.get('color', 'call')
        size = searchDict.get('size', 'siall')
        star = searchDict.get('star', 'stall')
        href = '%s_%s_%s_%s.png' % (masin, color, size, star)
        r = HttpResponse(href)
        return r
