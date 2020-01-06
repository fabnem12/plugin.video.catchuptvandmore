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

from codequick import Route, Resolver, Listitem, utils, Script

from resources.lib.labels import LABELS
from resources.lib import web_utils
from resources.lib import download
from resources.lib.listitem_utils import item_post_treatment

import json
import re
import urlquick

# TO DO

URL_ROOT = 'http://www.la7.it'

URL_DAYS = URL_ROOT + '/rivedila7/0/%s'
# Channels (upper)

# Live
URL_LIVE = URL_ROOT + '/dirette-tv'


def replay_entry(plugin, item_id, **kwargs):
    """
    First executed function after replay_bridge
    """
    return list_days(plugin, item_id)


@Route.register
def list_days(plugin, item_id, **kwargs):
    """
    Build programs listing
    - Les feux de l'amour
    - ...
    """
    resp = urlquick.get(URL_DAYS % item_id.upper())
    root = resp.parse(
        "div", attrs={
            "class": "wrapper-nav wrapper-nav-%s" % item_id
        })

    for day_datas in root.find(".//div[@class='content']").iterfind(".//a"):
        day_title = day_datas.find(".//div[@class='giorno-text']").text.strip(
        ) + ' - ' + day_datas.find(".//div[@class='giorno-numero']").text.strip(
        ) + ' - ' + day_datas.find(
            ".//div[@class='giorno-mese']").text.strip()
        day_url = URL_ROOT + day_datas.get('href')

        item = Listitem()
        item.label = day_title
        item.set_callback(list_videos, item_id=item_id, day_url=day_url)
        item_post_treatment(item)
        yield item


@Route.register
def list_videos(plugin, item_id, day_url, **kwargs):

    resp = urlquick.get(day_url)
    root = resp.parse()

    for video_datas in root.iterfind(".//div[@class='item item--guida-tv']"):
        if video_datas.find(".//div[@class='label-no-replica']") is None:
            video_title = video_datas.find(".//h2").text.strip()
            video_image = 'https:' + video_datas.find(
                ".//div[@class='bg-img lozad']").get('data-background-image')
            video_plot = ''
            if video_datas.find(".//div[@class='occhiello']").text is not None:
                video_plot = video_datas.find(
                    ".//div[@class='occhiello']").text.strip()
            video_url = video_datas.find(".//a").get('href')

            item = Listitem()
            item.label = video_title
            item.art['thumb'] = video_image
            item.info['plot'] = video_plot

            item.set_callback(
                get_video_url,
                item_id=item_id,
                video_url=video_url)
            item_post_treatment(item, is_playable=True, is_downloadable=True)
            yield item


@Resolver.register
def get_video_url(plugin,
                  item_id,
                  video_url,
                  download_mode=False,
                  **kwargs):

    resp = urlquick.get(video_url, max_age=-1)
    json_value = re.compile(r'src\: \{(.*?)\}\,').findall(resp.text)[0]
    json_parser = json.loads('{' + json_value + '}')
    if download_mode:
        return download.download_video(json_parser["m3u8"].replace(
            'http://la7-vh.akamaihd.net/i/,/content',
            'https://vodpkg.iltrovatore.it/local/hls/,/content').replace(
                'csmil', 'urlset'))
    return json_parser["m3u8"].replace(
        'http://la7-vh.akamaihd.net/i/,/content',
        'https://vodpkg.iltrovatore.it/local/hls/,/content').replace(
            'csmil', 'urlset')


def live_entry(plugin, item_id, **kwargs):
    return get_live_url(plugin, item_id, item_id.upper())


@Resolver.register
def get_live_url(plugin, item_id, video_id, **kwargs):

    resp = urlquick.get(URL_LIVE, max_age=-1)
    if 'http' in re.compile(r'var vS \= \"(.*?)\"').findall(resp.text)[0]:
        return re.compile(r'var vS \= \"(.*?)\"').findall(resp.text)[0]
    else:
        return 'https:' + re.compile(r'var vS \= \"(.*?)\"').findall(resp.text)[0]
