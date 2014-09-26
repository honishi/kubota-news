#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import logging.config
import ConfigParser
import time
import re

from twython import Twython
from twython import TwythonError
import MeCab


NEWS_CONFIGURATION = os.path.dirname(os.path.abspath(__file__)) + '/news.configuration'
DEBUG_DRY_RUN = False

INITIAL_SINCE_ID = 1


# main sequence
def main():
    init_logging(NEWS_CONFIGURATION)
    (source_screen_names, polling_interval, last_names, first_names,
     ckey, csecret, akey, asecret) = load_configuration(NEWS_CONFIGURATION)

    logging.info(u"source_screen_names:<{}> polling_interval:<{}>"
                 .format(source_screen_names, polling_interval))
    logging.info(u"last_names:<{}> first_names:<{}>".format(last_names, first_names))
    logging.info(u"ck:{} cs:{} ak:{} as:{}".format(ckey, csecret, akey, csecret))

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
                        if DEBUG_DRY_RUN:
                            logging.info(u"DRY_RUN: skip updating status")
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


# internal methods
def init_logging(configuration_file):
    logging.config.fileConfig(configuration_file)


def load_configuration(configuration_file):
    config = ConfigParser.ConfigParser()
    config.read(configuration_file)

    section = 'news'
    source_screen_names = config.get(section, 'source_screen_names').split(',')
    polling_interval = int(config.get(section, 'polling_interval'))

    last_names = unicode(config.get(section, 'last_names'), 'utf-8').split(',')
    first_names = unicode(config.get(section, 'first_names'), 'utf-8').split(',')

    consumer_key = config.get(section, 'consumer_key')
    consumer_key = config.get(section, 'consumer_key')
    consumer_secret = config.get(section, 'consumer_secret')
    access_key = config.get(section, 'access_key')
    access_secret = config.get(section, 'access_secret')

    return (source_screen_names, polling_interval, last_names, first_names,
            consumer_key, consumer_secret, access_key, access_secret)


def rewrite(original_text, last_names, first_names):
    replace_maps = []
    person_index = -1

    tagger = MeCab.Tagger("")

    # unicode -> str
    original_text_str = original_text.encode('utf-8')

    node = tagger.parseToNode(original_text_str)

    while node:
        # str -> unicode
        surface = unicode(node.surface, 'utf-8')
        posid = node.posid
        # feature = unicode(node.feature, 'utf-8')
        # logging.debug(u"surface:<{}> posid:<{}> feature:<{}>".format(surface, posid, feature))

        if posid == 43:
            person_index += 1
            replace_maps.append((surface, name_at_index(last_names, person_index)))
        elif posid == 44:
            replace_maps.append((surface, name_at_index(first_names, person_index)))

        node = node.next

    is_rewrited = False
    rewrited_text = None

    if 0 < len(replace_maps):
        is_rewrited = True
        rewrited_text = original_text

        for (pattern, repl) in replace_maps:
            # logging.debug(u"pattern:{} repl:{}".format(pattern, repl))
            rewrited_text = re.sub(pattern, repl, rewrited_text)

        rewrited_text = post_filter(rewrited_text)

    return (is_rewrited, rewrited_text)


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


if __name__ == '__main__':
    main()
