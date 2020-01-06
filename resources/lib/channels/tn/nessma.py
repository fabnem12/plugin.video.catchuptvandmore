# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2018  SylvainCecchetto

    This file is part of Catch-up TV & More.

    Catch-up TV & More is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    Catch-up TV & More is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with Catch-up TV & More; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

# The unicode_literals import only has
# an effect on Python 2.
# It makes string literals as unicode like in Python 3
from __future__ import unicode_literals

from builtins import str
from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS
from resources.lib import web_utils
from resources.lib import resolver_proxy
from resources.lib.listitem_utils import item_post_treatment

import re
import urlquick

# TO DO
# Add Replays/Serie TV (required account)

# Live
URL_ROOT = 'https://www.nessma.tv'

URL_LIVE = URL_ROOT + '/live'

URL_REPLAY = URL_ROOT + '/ar/replays'

URL_VIDEOS = URL_ROOT + '/ar/videos'


def replay_entry(plugin, item_id, **kwargs):
    """
    First executed function after replay_bridge
    """
    return list_categories(plugin, item_id)


@Route.register
def list_categories(plugin, item_id, **kwargs):
    """
    Build categories listing
    """
    item = Listitem()
    item.label = 'الفيديوهات'
    item.set_callback(list_videos, item_id=item_id, page='1')
    item_post_treatment(item)
    yield item

    item = Listitem()
    item.label = 'مشاهدة الحلقات'
    item.set_callback(list_programs, item_id=item_id)
    item_post_treatment(item)
    yield item


@Route.register
def list_programs(plugin, item_id, **kwargs):
    """
    Build progams listing
    - Le JT
    - ...
    """
    resp = urlquick.get(URL_REPLAY)
    root = resp.parse()

    for program_datas in root.iterfind(".//div[@class='col-sm-3']"):
        if program_datas.find('.//img').get('alt') is not None:
            program_title = program_datas.find('.//img').get('alt')
            program_image = program_datas.find('.//img').get('src')
            program_url = program_datas.find('.//a').get('href')

            item = Listitem()
            item.label = program_title
            item.art['thumb'] = program_image

            item.set_callback(list_videos_replays,
                              item_id=item_id,
                              program_url=program_url,
                              page='1')
            item_post_treatment(item)
            yield item


@Route.register
def list_videos_replays(plugin, item_id, program_url, page, **kwargs):

    resp = urlquick.get(program_url + '?page=%s' % (page))
    root = resp.parse()

    if root.find(".//div[@class='row replaynessma-cats row-eq-height ']") is not None:
        root2 = resp.parse("div", attrs={"class": "row replaynessma-cats row-eq-height "})
        for video_datas in root2.iterfind(".//article"):
            video_title = video_datas.find('.//h3/a').text
            video_image = video_datas.find('.//img').get('src')
            video_url = video_datas.find('.//a').get('href')

            item = Listitem()
            item.label = video_title
            item.art['thumb'] = video_image

            item.set_callback(get_video_url,
                              item_id=item_id,
                              video_url=video_url)
            item_post_treatment(item, is_playable=True, is_downloadable=True)
            yield item
    else:
        for video_datas in root.iterfind(".//div[@class='col-sm-3']"):
            video_title = video_datas.find('.//img').get('alt')
            video_image = video_datas.find('.//img').get('src')
            video_url = video_datas.find('.//a').get('href')

            item = Listitem()
            item.label = video_title
            item.art['thumb'] = video_image

            item.set_callback(get_video_url,
                              item_id=item_id,
                              video_url=video_url)
            item_post_treatment(item, is_playable=True, is_downloadable=True)
            yield item

        yield Listitem.next_page(item_id=item_id,
                                 program_url=program_url,
                                 page=str(int(page) + 1))


@Route.register
def list_videos(plugin, item_id, page, **kwargs):

    resp = urlquick.get(URL_VIDEOS + '?page=%s' % (page))
    root = resp.parse()

    for video_datas in root.iterfind(".//div[@class='col-sm-4']"):
        if video_datas.find('.//img') is not None:
            video_title = video_datas.find('.//img').get('alt')
            video_image = video_datas.find('.//img').get('src')
            video_url = video_datas.find('.//a').get('href')

            item = Listitem()
            item.label = video_title
            item.art['thumb'] = video_image

            item.set_callback(get_video_url,
                              item_id=item_id,
                              video_url=video_url)
            item_post_treatment(item, is_playable=True, is_downloadable=True)
            yield item

    yield Listitem.next_page(item_id=item_id,
                             page=str(int(page) + 1))


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  video_url,
                  download_mode=False,
                  **kwargs):

    resp = urlquick.get(video_url)
    video_id = re.compile(r'youtube\.com\/embed\/(.*.)\?').findall(
        resp.text)[0]

    return resolver_proxy.get_stream_youtube(plugin, video_id, download_mode)


def live_entry(plugin, item_id, **kwargs):
    return get_live_url(plugin, item_id, item_id.upper())


@Resolver.register
def get_live_url(plugin, item_id, video_id, **kwargs):

    resp = urlquick.get(URL_LIVE)
    live_id = re.compile(r'dailymotion.com/embed/video/(.*?)[\?\"]').findall(
        resp.text)[0]
    return resolver_proxy.get_stream_dailymotion(plugin, live_id, False)
