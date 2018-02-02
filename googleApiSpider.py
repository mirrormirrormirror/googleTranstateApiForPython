import requests
import re
from urllib.parse import urlencode
import execjs
import sys
import getopt
import os


class googleApiCrawler:
    def __init__(self, sl, tl, keyword, translateUrl="https://translate.google.cn/translate_a/single?"):
        self.translateUrl = translateUrl
        self.sl = sl
        self.tl = tl
        self.keyword = keyword
        self.tkkUrl = "https://translate.google.cn/"

    def getTkk(self):
        googleApiPage = requests.get(self.tkkUrl)
        par = re.compile("TKK=eval\('\((.*?)\)'\)")
        result = re.search(par, googleApiPage.text)
        jsScript = result.group(1)
        jsScript = jsScript.replace("\\x3d", "=").replace("\\x27", "'")
        tKK = execjs.eval(jsScript)
        return tKK

    def getTk(self):
        tkJsScript = '''
                        var b = function (a, b) {
                        for (var d = 0; d < b.length - 2; d += 3) {
                            var c = b.charAt(d + 2),
                                c = "a" <= c ? c.charCodeAt(0) - 87 : Number(c),
                                c = "+" == b.charAt(d + 1) ? a >>> c : a << c;
                            a = "+" == b.charAt(d) ? a + c & 4294967295 : a ^ c
                        }
                        return a
                        }
                        function getTk(a,TKK) {
                        for (var e = TKK.split("."), h = Number(e[0]) || 0, g = [], d = 0, f = 0; f < a.length; f++) {
                            var c = a.charCodeAt(f);
                            128 > c ? g[d++] = c : (2048 > c ? g[d++] = c >> 6 | 192 : (55296 == (c & 64512) && f + 1 < a.length && 56320 == (a.charCodeAt(f + 1) & 64512) ? (c = 65536 + ((c & 1023) << 10) + (a.charCodeAt(++f) & 1023), g[d++] = c >> 18 | 240, g[d++] = c >> 12 & 63 | 128) : g[d++] = c >> 12 | 224, g[d++] = c >> 6 & 63 | 128), g[d++] = c & 63 | 128)
                        }
                        a = h;
                        for (d = 0; d < g.length; d++) a += g[d], a = b(a, "+-a^+6");
                        a = b(a, "+-3^+b+-f");
                        a ^= Number(e[1]) || 0;
                        0 > a && (a = (a & 2147483647) + 2147483648);
                        a %= 1E6;
                        return a.toString() + "." + (a ^ h)}
                    '''
        fun = execjs.compile(tkJsScript)
        tk = fun.call('getTk', self.keyword, self.getTkk())
        return tk

    def crawl(self):
        tk = self.getTk()

        data = [
            ('client', 't'),
            ('sl', self.sl),
            ('tl', self.tl),
            ('hl', 'zh-CN'),
            ('dt', 't'),
            ('ie', 'UTF-8'),
            ('oe', 'UTF-8'),
            ('tk', tk),
            ('q', self.keyword)]
        googleTranslateUrl = self.translateUrl + urlencode(data)
        googleTranslatePage = requests.get(googleTranslateUrl)
        textPar = re.compile('\[\[\["(.*?)","')
        translateText = textPar.search(googleTranslatePage.text).group(1)
        return translateText


def printInfo():
    print("-i,表示输入语言的种类，必填项")
    print("-o,表示翻译目标语言的种类，必填项")
    print("-q,表示待翻译的词，必填项")
    print("-h 或则 -help 获取帮助")


if __name__ == "__main__":
    sl = None
    tl = None
    keyword = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:q:h:help")
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    print(opts)
    print(args)
    for o, a in opts:
        if o == "-i":
            sl = a
        elif o == "-o":
            tl = a
        elif o == "-q":
            keyword = a
    if args[0] in ('-h',"-help"):
        printInfo()


    testInfo0 = {"sl": "en", "tl": "uk", "keyword": "hello"}
    # 中翻译成俄语
    testInfo1 = {"sl": "zh-CN", "tl": "ru", "keyword": "鸡蛋"}
    # 俄语翻译成英语
    testInfo2 = {"sl": "ru", "tl": "en", "keyword": "телевидение"}
    testInfo = {"sl": sl, "tl": tl, "keyword": keyword}
    crawl = googleApiCrawler(sl=testInfo['sl'], tl=testInfo['tl'], keyword=testInfo['keyword'])
    language = crawl.crawl()
    print(language)
