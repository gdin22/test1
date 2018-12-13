# -*- coding:utf-8 -*-
import sys
import os.path
from PyQt4 import QtGui, QtCore, QtWebKit
import re
from PIL import Image
import os

"""
可以截网站的全图
"""


class PageShotter(QtGui.QWidget):
    def __init__(self, url, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.url = url

    def shot(self):
        webView = QtWebKit.QWebView(self)
        webView.load(QtCore.QUrl(self.url))
        self.webPage = webView.page()
        self.connect(webView, QtCore.SIGNAL("loadFinished(bool)"), self.savePage)

    def savePage(self, finished):
        # print finished
        if finished:
            print(u"开始截图！")
            size = self.webPage.mainFrame().contentsSize()
            print(u"页面宽：%d，页面高：%d" % (size.width(), size.height()))
            self.webPage.setViewportSize(QtCore.QSize(size.width() + 16, size.height()))
            img = QtGui.QImage(size, QtGui.QImage.Format_ARGB32)
            painter = QtGui.QPainter(img)
            self.webPage.mainFrame().render(painter)
            painter.end()
            print(self.url)
            page = re.findall('page=(.*?)&keywords=(.*)', self.url)[0][0]
            key = re.findall('page=(.*?)&keywords=(.*)', self.url)[0][1]
            fileName = "%s_%s.png" % (key, page)
            fileName = os.path.join('static', fileName)
            if img.save(fileName):
                filePath = os.path.join(os.path.dirname(__file__), fileName)

                print("截图完毕：%s" % filePath)
                getHeadShot(filePath, size.width())
            else:
                print(u"截图失败")
        else:
            print(u"网页加载失败！")
        self.close()


def getHeadShot(filePath, width):
    image = Image.open(filePath)
    region = image.crop((0, 0, width, 1200))
    newFilePathList = filePath.split('.')
    newFilePath = ''.join([newFilePathList[0], '_head.', newFilePathList[1]])
    region.save(newFilePath)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    # shotter = PageShotter("http://www.adssfwewfdsfdsf.com")
    shotter = PageShotter(sys.argv[1])
    shotter.shot()
    sys.exit(app.exec_())
