import pyxel


def text_mc(x, y, text_list, color_list):
    '''
    複数の色で文字を描画する
    :param x: 描画位置
    :param y: 描画位置
    :param text_list: 表示する文字のリスト
    :param color_list: 対応するtext_listの文字の色のリスト
    :return:
    '''
    TEXT_W = 4
    for i, s in enumerate(text_list):
        pyxel.text(x, y, s, color_list[i])
        x += len(s) * TEXT_W


def center(text, width):
    '''
    文章を中央揃えで表示する際のx座標を返す
    :param text: 座標を得たい文章
    :param width: 画面の幅
    :return:
    '''
    TEXT_W = 4
    return width // 2 - len(text) * TEXT_W // 2