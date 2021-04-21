import MeCab
import pandas as pd
import itertools
import collections
import seaborn
import matplotlib.pyplot as plt

# <MeCab インストール手順 mac版>
# 動作確認 : 2021/04/21
# Version : Python 3.7.1
# 前提条件 : brewがインストールされている。
#
# $ brew install mecab mecab-ipadic git curl xz ## MeCab関連に必要なものを格納している。
# $ pip install mecab-python3 ## python3にてMeCab動かすために必要なものを格納している。
# $ cd desktop ## デスクトップへ移動する。
# $ git clone --depth 1 git@github.com:neologd/mecab-ipadic-neologd.git ## MeCabを利用する際の辞書を作成するためのファイルをgitコマンドを活用してダウンロードする。
# $ cd mecab-ipadic-neologd ## ディレクトリ移動
# $ ./bin/install-mecab-ipadic-neologd -n ## ファイル実行して、辞書ファイル生成を行う。
# mecab-ipadic-neologd ファイルを削除する。
# $ echo `mecab-config --dicdir`"/mecab-ipadic-neologd" ## MeCabの辞書ファイルが格納されているパスを取得する
# MeCab.Tagger("-d xxx -O chasen")のxxx箇所へ上記のパスを貼り付ける
#
# mecab-python3のエラー対策集 : https://github.com/SamuraiT/mecab-python3#common-issues
# error message: [ifs] no such file or directory: /usr/local/etc/xxx : MeCabを実行して、上のようなエラーが発生したら、touch /usr/local/etc/xxx と実行して空ファイルを生成してください。
#
# <参考>
# mecab-ipadic-neologdに関する記事 : https://analytics-note.xyz/mac/neologd-install/
# mecabインストールまでの流れ : https://qiita.com/paulxll/items/72a2bea9b1d1486ca751
# ChaSen : 奈良先端科学技術大学院で開発された形態素解析ツールです。(https://nzigen.com/ysawa/mecab-chasen-kytea-juman-install/)
mecab = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd -O chasen")

# 文章を形態素解析を使って解読する
# 名詞、動詞、形容詞に分解する
def wordAnalytics(text):
    # テキストを形態素解析して単語単位をノードとして扱う。
    # ノード : https://www.kagoya.jp/howto/rentalserver/node/
    node = mecab.parseToNode(text)
    meishiList = []
    doshiList = []
    keiyoshiList = []
    # ノードが存在する(単語が存在する数)だけwhileされる。
    # node.surface : 形態素の文字列情報
    # node.feature : CSVで表記された素性情報(データを分類する際に役立つ情報)
    # featureの中身 : [品詞, 品詞細分類1, 品詞細分類2, 品詞細分類3, 活用形, 活用型, 原形, 読み, 発音]
    while node:
        hinshi = node.feature.split(",")[0]
        if hinshi == "名詞":
            meishiList.append(node.surface)
        elif hinshi == "動詞":
            doshiList.append(node.feature.split(",")[6])
        elif hinshi == "形容詞":
            keiyoshiList.append(node.feature.split(",")[6])

        node = node.next

    # Series : https://docs.pyq.jp/python/pydata/pandas/series.html
    return pd.Series([meishiList, doshiList, keiyoshiList])

if __name__ == "__main__":
    # data.csvファイルを呼び出す
    df = pd.read_csv('./data.csv')
    # 本文をwordAnalyticsの引数として持たせる。
    # 戻り値として[[名詞1, 名詞2, ...], [動詞1, 動詞2, ...], [形容詞1, 形容詞2, ...]]が返ってくるので、それに合うような形式でデータを受け取る。
    # apply : https://qiita.com/hisato-kawaji/items/0c66969343a196a65cee
    df[["名詞", "動詞", "形容詞"]] = df["本文"].apply(wordAnalytics)

    # 2次元に格納される動詞を1次元に変更する。
    wordList = list(itertools.chain.from_iterable(df["動詞"]))
    # [('単語1', 出現回数), ('単語2', 出現回数)] とする
    c = collections.Counter(wordList)

    # フォントファミリーを設定する。日本語表示に対応するため。
    # macにてフォントファミリーの調べ方 : https://openbook4.me/sections/1674
    plt.rcParams['font.family'] = 'Hiragino Sans'

    # グラフの作成
    # figsize : (幅, 高さ) ピクセル単位
    fig = plt.subplots(figsize=(8, 10))
    # matplotlibの内部で動いているもの
    # setに関する詳細 : https://note.nkmk.me/python-matplotlib-seaborn-basic/
    seaborn.set(font="Hiragino Sans", context="talk", style="white")
    # 上位20個の単語に対して出力を行う。
    # yを設定することで、横方向へグラフ化する。
    # https://pythondatascience.plavox.info/seaborn/%E6%A3%92%E3%82%B0%E3%83%A9%E3%83%95
    seaborn.countplot(y=wordList, order=[word[0] for word in c.most_common(20)], palette="deep")
    # 画像の書き出し処理を行う。
    plt.savefig("./result.png")
