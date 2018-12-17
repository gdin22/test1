from django.shortcuts import render, HttpResponse, redirect
from contact.models import Contacts, SaveKeys
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.http import HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import xlrd
import time
import xlwt
import xlrd
# Create your views here.


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


def getExcelMessage(fileName):
    workbook = xlrd.open_workbook(fileName)
    sheet = workbook.sheet_by_index(0)
    col0 = sheet.col_values(0)
    urls = []
    for key in col0:
        urls.append('https://www.amazon.com/s/ref=sr_pg_2?page=%s&keywords=%s' % ('1', key))
        urls.append('https://www.amazon.com/s/ref=sr_pg_2?page=%s&keywords=%s' % ('2', key))
    return urls, col0


def screenshot(urls):
    for url in urls:
        os.system(r'python contact/screenShot.py "%s"' % url)


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
