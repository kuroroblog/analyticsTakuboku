from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time

# 作品詳細ページへアクセスして、html形式で情報を取得する
def getText(articleId):
    # api接続を頻繁に行うことで障害を与えないためにも一定時間を置きながら、アクセスする。
    time.sleep(3)
    # 青空文庫APIについて : https://qiita.com/ksato9700/items/626cc82c007ba8337034
    res = requests.get("http://pubserver2.herokuapp.com/api/v0.1/books/" + str(articleId) + "/content?format=html")
    soup = BeautifulSoup(res.content, "html.parser")
    title = soup.find("title").text
    # div要素内のmain_textとして書かれている文章を抽出する。
    doc = soup.find("div", {"class" : "main_text"}).text
    return title, doc

# 記事一覧情報から作品IDを取得する
def getArticleIdList(articleList):
    # 新字新仮名のみを扱う。
    # [新字新仮名、作品ID：111, 新字新仮名、作品ID：222]みたいな形で入ってくる。
    idList = re.findall("新字新仮名、作品ID：[0-9]+", articleList)
    # 配列内の作品IDだけを取得するために、:区切りで配列にしてindexが1番目の要素を取得するようにする。
    # そして再度配列を生成して格納していく。
    return [id.split("：")[1] for id in idList]

# 作者IDに紐づく、記事一覧を取得する
def getArticleList(num):
    # 青空文庫APIについて : https://qiita.com/ksato9700/items/626cc82c007ba8337034
    res = requests.get("https://www.aozora.gr.jp/index_pages/person" + str(num) + ".html")
    soup = BeautifulSoup(res.content, "html.parser")
    # find : https://uxmilk.jp/8683
    return soup.find("ol").text

if __name__ == "__main__":
    # 石川啄木作品の記事一覧ページへアクセスし、一覧情報を取得する
    articleList = getArticleList(153)
    # 記事一覧情報から作品IDを取得する
    articleIdList = getArticleIdList(articleList)

    docList = []
    for articleId in articleIdList:
        title, doc = getText(articleId)
        docList.append([title, doc])

    # DataFrame : https://ai-inter1.com/pandas-dataframe_basic/
    dfDoc = pd.DataFrame(docList, columns=["作品名", "本文"])
    # data.csvとしてcsv吐き出し
    # ※ data.csvに格納されているデータを、ローカルにて検証するために利用します。2次利用はしません。
    dfDoc.to_csv('./data.csv')
