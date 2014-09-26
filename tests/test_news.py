#!/usr/bin/env python
# -*- coding: utf-8 -*-

import news
import pytest

LAST_NAMES = u"久保田,森,佐野,国場".split(u',')
FIRST_NAMES = u"学,義之,智則,雄太".split(u',')

@pytest.mark.parametrize(("input", "expected"), [
    (u"私は中村です。",
     u"私は久保田です。"),
    (u"競泳男子１５００ｍ自由形 山本が銀 http://t.co/t6hg7K89W6 #nhk_news",
     u"競泳男子１５００ｍ自由形 久保田が銀 http://t.co/t6hg7K89W6 #nhk_news"),
    (u"大相撲秋場所 幕下は安彦が優勝 http://t.co/5thDRm7u4W #nhk_news",
     u"大相撲秋場所 幕下は学が優勝 http://t.co/5thDRm7u4W #nhk_news"),
    (u"太郎、中村太郎、田中、二郎",
     u"学、久保田学、森、義之"),
    (u"【里崎 知られざる「野村超え」】千葉ロッテの里崎には、野村克也氏や古田敦也氏など名捕手を上回る記録があった。",
     u"【里崎 知られざる「久保田超え」】千葉ロッテの里崎には、久保田学氏や森義之也氏など名捕手を上回る記録があった。"),
    (u"【高橋真麻 結婚の生野アナ祝福】フリーアナウンサーの高橋真麻が、結婚した生野アナをブログで祝福。生野アナは同期の中村アナと結婚。",
     u"【久保田学 結婚の森アナ祝福】フリーアナウンサーの久保田学が、結婚した森アナをブログで祝福。森アナは同期の佐野アナと結婚。"),
])
def test_rewrite(input, expected):
    (is_rewrited, rewrited) = news.rewrite(input, LAST_NAMES, FIRST_NAMES)
    assert (rewrited == expected)
