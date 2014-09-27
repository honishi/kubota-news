#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config
import re
import time

from twython import Twython
from twython import TwythonError
import MeCab

INITIAL_SINCE_ID = 1


def start(source_screen_names, polling_interval, last_names, first_names,
          ckey, csecret, akey, asecret, dry_run=False):
    since_ids = {}
    for source_screen_name in source_screen_names:
        since_ids[source_screen_name] = INITIAL_SINCE_ID

    while True:
        try:
            for source_screen_name in source_screen_names:
                logging.info(u"source_screen_name:{} since_id:{}"
                             .format(source_screen_name, since_ids[source_screen_name]))

                twitter = Twython(ckey, csecret, akey, asecret)
                statuses = twitter.get_user_timeline(screen_name=source_screen_name,
                                                     since_id=since_ids[source_screen_name])
                # logging.debug(statuses)

                for status in statuses:
                    status_id = status['id']
                    text = status['text']

                    collecting_since_id = (since_ids[source_screen_name] == INITIAL_SINCE_ID)
                    since_ids[source_screen_name] = max(since_ids[source_screen_name], status_id)

                    if collecting_since_id:
                        logging.debug(u"collected since_id {} skip rewriting"
                                      .format(since_ids[source_screen_name]))
                        break

                    (is_rewrited, rewrited_text) = rewrite(text, last_names, first_names)
                    log_status(status_id, text, is_rewrited, rewrited_text)

                    if is_rewrited:
                        if dry_run:
                            logging.info(u"dry_run: skip updating status")
                        else:
                            update_status(twitter, rewrited_text)
                        time.sleep(5)

        except Exception as exception:
            logging.error(u"caught exception:{}".format(exception))

        logging.debug(u"sleeping {} seconds...".format(polling_interval))
        time.sleep(polling_interval)


def log_status(status_id, text, is_rewrited, rewrited_text):
    logging.debug(u"id:{}".format(status_id))
    logging.debug(u"is_rewrited:{}".format(is_rewrited))
    logging.debug(u"original:{}".format(text))
    if is_rewrited:
        logging.debug(u"rewrited:{}".format(rewrited_text))


def update_status(twitter, text):
    logging.info(u"updating status:{}".format(text))

    try:
        twitter.update_status(status=text)
    except TwythonError as error:
        logging.debug(u"caught twitter error:{}".format(error))
        if re.search(r"duplicate", error.msg):
            logging.warning(u"ignoring duplicate update.")
        else:
            raise


def rewrite(original_text, last_names, first_names):
    is_rewrited = False
    rewrited_text = None

    replace_maps = create_replace_maps(original_text, last_names, first_names)
    # print(replace_maps)

    if 0 < len(replace_maps):
        is_rewrited = True
        rewrited_text = original_text

        for replace_map in replace_maps:
            [(last_name_pattern, first_name_pattern),
             (last_name_repl, first_name_repl)] = replace_map
            for (pattern, repl) in [(last_name_pattern, last_name_repl),
                                    (first_name_pattern, first_name_repl)]:
                logging.debug(u"pattern:{} repl:{}".format(pattern, repl))
                if pattern:
                    rewrited_text = re.sub(pattern, repl, rewrited_text)

        rewrited_text = post_filter(rewrited_text)

    return (is_rewrited, rewrited_text)


def create_replace_maps(original_text, last_names, first_names):
    """
    returns maps between patterns and replacements.
    replace_maps = [
        [('sato',  None   ), ('kubota', 'manabu'   )],
        [( None,  'jiro'  ), ('mori',   'yoshiyuki')],
        [('kato', 'saburo'), ('sano',   'tomonori' )],
    ]
    """
    replace_maps = []
    name_index = 0
    last_last_name = None
    last_first_name = None

    original_text_str = original_text.encode('utf-8')   # unicode -> str
    tagger = MeCab.Tagger("")
    node = tagger.parseToNode(original_text_str)

    while node:
        pattern = unicode(node.surface, 'utf-8')    # str -> unicode
        posid = node.posid
        # feature = unicode(node.feature, 'utf-8')
        # logging.debug(u"surface:<{}> posid:<{}> feature:<{}>".format(pattern, posid, feature))

        node = node.next

        # last name (43)
        if posid == 43:
            last_last_name = pattern
        # first name (44)
        elif posid == 44:
            last_first_name = pattern
        # neither last name nor first name
        else:
            if not last_last_name and not last_first_name:
                continue

            replace_map = replace_map_for_pattern(replace_maps, last_last_name, last_first_name)

            if not replace_map:
                # print(u'new')
                last_name_repl = name_at_index(last_names, name_index)
                first_name_repl = name_at_index(first_names, name_index)
                name_index += 1

                replace_map = [(last_last_name, last_first_name),
                               (last_name_repl, first_name_repl)]
                replace_maps.append(replace_map)
            else:
                # print(u'update')
                map_index = replace_maps.index(replace_map)

                [(last_name_pattern, first_name_pattern), repls] = replace_map
                updated_replace_map = [
                    (last_last_name if last_last_name else last_name_pattern,
                     last_first_name if last_first_name else first_name_pattern),
                    repls]

                replace_maps[map_index] = updated_replace_map

            last_last_name = None
            last_first_name = None

    return replace_maps


def replace_map_for_pattern(replace_maps, last_name_pattern=None, first_name_pattern=None):
    for replace_map in replace_maps:
        [(existing_last_name_pattern, existing_first_name_pattern),
         (last_name_repl, first_name_repl)] = replace_map

        found_last_name_pattern = False
        found_first_name_pattern = False

        if existing_last_name_pattern and last_name_pattern:
            found_last_name_pattern = (existing_last_name_pattern == last_name_pattern)

        if existing_first_name_pattern and first_name_pattern:
            found_first_name_pattern = (existing_first_name_pattern == first_name_pattern)

        if (found_last_name_pattern or found_first_name_pattern):
            return replace_map

    return None


def name_at_index(names, index=0):
    if (len(names) - 1) < index:
        index = 0

    return names[index]


def post_filter(text):
    filtered = text
    filters = [(u"&amp;", u"&")]

    for (pattern, repl) in filters:
        filtered = re.sub(pattern, repl, filtered)

    return filtered
