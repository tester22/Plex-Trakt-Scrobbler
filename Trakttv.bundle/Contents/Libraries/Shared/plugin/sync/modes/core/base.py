from plugin.sync import SyncMedia, SyncData

import itertools
import logging

log = logging.getLogger(__name__)

TRAKT_DATA_MAP = {
    SyncMedia.Movies: [
        SyncData.Collection,
        SyncData.Playback,
        SyncData.Ratings,
        SyncData.Watched,
        # SyncData.Watchlist
    ],
    SyncMedia.Shows: [
        SyncData.Ratings
    ],
    SyncMedia.Seasons: [
        SyncData.Ratings
    ],
    SyncMedia.Episodes: [
        SyncData.Collection,
        SyncData.Playback,
        SyncData.Ratings,
        SyncData.Watched,
        # SyncData.Watchlist
    ]
}

class Mode(object):
    mode = None
    children = []

    def __init__(self, main):
        self.__main = main

        self.children = [c(self) for c in self.children]

    @property
    def current(self):
        return self.__main.current

    @property
    def handlers(self):
        return self.__main.handlers

    @property
    def modes(self):
        return self.__main.modes

    @property
    def plex(self):
        if not self.current or not self.current.state:
            return None

        return self.current.state.plex

    @property
    def trakt(self):
        if not self.current or not self.current.state:
            return None

        return self.current.state.trakt

    def run(self):
        raise NotImplementedError

    def execute_children(self):
        for c in self.children:
            c.run()

    def execute_handlers(self, media, data, *args, **kwargs):
        if type(media) is not list:
            media = [media]

        if type(data) is not list:
            data = [data]

        for m, d in itertools.product(media, data):
            if d not in self.handlers:
                log.debug('Unknown sync data: %r', d)
                continue

            try:
                self.handlers[d].run(m, self.mode, *args, **kwargs)
            except Exception, ex:
                log.warn('Exception raised in handlers[%r].run(%r, ...): %s', d, m, ex, exc_info=True)


def log_unsupported_guid(logger, rating_key, p_guid, p_item, dictionary=None):
    if dictionary is not None:
        if rating_key in dictionary:
            return

        dictionary[rating_key] = True

    title = p_item.get('title')
    year = p_item.get('year')

    if title and year:
        logger.info('[%r] GUID agent %r is not supported on: %r (%r)', rating_key, p_guid.agent, title, year)
    else:
        logger.info('[%r] GUID agent %r is not supported', rating_key, p_guid.agent)
