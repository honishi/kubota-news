#!/usr/bin/env python
# -*- coding: utf-8 -*-

import news
import pytest

LAST_NAMES = u"久保田,森,佐野,国場".split(u',')
FIRST_NAMES = u"学,義之,智則,雄太".split(u',')


def create_names(last_names, first_names):
    names = []

    for index in xrange(len(last_names)):
        names.append((last_names[index], first_names[index]))

    return names


@pytest.mark.parametrize(("input", "expected"), [
    (u"私は中村です。",
     u"私は久保田です。"),
    (u"競泳男子１５００ｍ自由形 山本が銀 http://t.co/t6hg7K89W6 #nhk_news",
     u"競泳男子１５００ｍ自由形 久保田が銀 http://t.co/t6hg7K89W6 #nhk_news"),
    (u"大相撲秋場所 幕下は安彦が優勝 http://t.co/5thDRm7u4W #nhk_news",
     u"大相撲秋場所 幕下は学が優勝 http://t.co/5thDRm7u4W #nhk_news"),
    (u"太郎、中村太郎、田中、二郎",
     u"学、久保田学、森、智則"),
    (u"太郎、中村太郎、田中、二郎、田中二郎",
     u"学、久保田学、森、義之、森義之"),
    (u"【里崎 知られざる「野村超え」】千葉ロッテの里崎には、野村克也氏や古田敦也氏など名捕手を上回る記録があった。",
     u"【里崎 知られざる「久保田超え」】千葉ロッテの里崎には、久保田学氏や森義之也氏など名捕手を上回る記録があった。"),
    (u"【高橋真麻 結婚の生野アナ祝福】フリーアナウンサーの高橋真麻が、結婚した生野アナをブログで祝福。生野アナは同期の中村アナと結婚。",
     u"【久保田学 結婚の森アナ祝福】フリーアナウンサーの久保田学が、結婚した森アナをブログで祝福。森アナは同期の佐野アナと結婚。"),
    (u"【なんでや 牛島氏が香川氏悼む】元プロ野球選手「ドカベン」香川伸行氏が死去。浪商時代バッテリーを組んだ牛島和彦氏は「寂しい」と胸中。",
     u"【なんでや 久保田氏が森氏悼む】元プロ野球選手「ドカベン」森義之氏が死去。浪商時代バッテリーを組んだ久保田学氏は「寂しい」と胸中。"),
    (u"一郎、二郎、三郎、佐藤二郎、田中一郎、加藤三郎",
     u"学、義之、智則、森義之、久保田学、佐野智則")
])
def test_rewrite(input, expected):
    names = create_names(LAST_NAMES, FIRST_NAMES)
    (is_rewrited, rewrited) = news.rewrite(input, names)
    assert (rewrited == expected)
