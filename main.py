#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import logging.config
import ConfigParser

import news


MAIN_CONFIGURATION = os.path.dirname(os.path.abspath(__file__)) + '/main.configuration'


# main sequence
def main():
    init_logging(MAIN_CONFIGURATION)
    (source_screen_names, polling_interval, names,
     ckey, csecret, akey, asecret, dry_run) = load_configuration(MAIN_CONFIGURATION)

    logging.info(u"source_screen_names:<{}> polling_interval:<{}>"
                 .format(source_screen_names, polling_interval))
    logging.info(u"names:<{}>".format(names))
    logging.info(u"ck:{} cs:{} ak:{} as:{}".format(ckey, csecret, akey, csecret))

    news.start(source_screen_names, polling_interval, names, ckey, csecret, akey, asecret, dry_run)


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

    if len(last_names) != len(first_names):
        raise Exception(u"invalid name parameter length.")

    names = []
    for index in xrange(len(last_names)):
        names.append((last_names[index], first_names[index]))

    consumer_key = config.get(section, 'consumer_key')
    consumer_key = config.get(section, 'consumer_key')
    consumer_secret = config.get(section, 'consumer_secret')
    access_key = config.get(section, 'access_key')
    access_secret = config.get(section, 'access_secret')

    dry_run = config.getboolean(section, 'dry_run')

    return (source_screen_names, polling_interval, names,
            consumer_key, consumer_secret, access_key, access_secret, dry_run)


if __name__ == '__main__':
    main()
