#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Catch-up TV & More
    Copyright (C) 2016  SylvainCecchetto

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

import sys

filepath = sys.argv[1]

print('Work on %s file' % filepath)

lines = []

with open(filepath, "r") as f:
    for line in f:
        lines.append(line)

new_lines = []

modules = []
for i in range(len(lines)):
    add_line = True
    if "'callback':" in lines[i]:
        lines[i] = lines[i].replace("'callback':", "'resolver':")

    if "'module':" in lines[i]:
        module = lines[i].split("module': '")[1].split("',")[0]
        module = module.replace('.', '/')
        modules.append(module)
        add_line = False

    if add_line:
        new_lines.append(lines[i])

cnt = 0
for i in range(len(new_lines)):
    add_line = True
    if "'resolver':" in new_lines[i]:
        new_lines[i] = new_lines[i].replace("live_bridge", '/' + modules[cnt] + ':get_live_url')
        cnt = cnt + 1



with open(filepath, 'w') as f:
    for line in new_lines:
        f.write(line)

