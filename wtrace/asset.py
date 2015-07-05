#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2015  Etienne Noreau-Hebert <e@zncb.io>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Generic representation for web assets. """

import hashlib

class Asset:

    CONTENT_TYPE_APP = "application"
    CONTENT_TYPE_AUDIO = "audio"
    CONTENT_TYPE_IMAGE = "image"
    CONTENT_TYPE_MESG = "message"
    CONTENT_TYPE_MULTI = "multipart"
    CONTENT_TYPE_TEXT = "text"
    CONTENT_TYPE_VIDEO = "video"
    
    # application
    CONTENT_SUBTYPE_JS = "javascript"
    CONTENT_SUBTYPE_XJS = "x-javascript"
    
    # audio

    # image
    CONTENT_SUBTYPE_PNG = "png"
    CONTENT_SUBTYPE_GIF = "gif"
    CONTENT_SUBTYPE_JPEG = "jpeg"

    # message

    # multipart

    # text
    CONTENT_SUBTYPE_HTML = "html"
    CONTENT_SUBTYPE_CSS = "css"

    # video

    
    def __init__(self):
        self.method = None
        self.scheme = None
        self.host = None
        self.port = None
        self.path = None
        self.type = None
        self.subtype = None
        self.ct_argument = None
        self.content = None
        self.size = None
        self.hashes = None
        self.start_time = None
        self.end_time = None
        self.stored_path = None

    def __str__(self):
        from utils import sizeof_fmt
        return "{hsh} {sz:8} {ct:24} [{h}]".format(h=self.host,\
                                                   ct="/".join([str(self.type),str(self.subtype)]),\
                                                   sz=sizeof_fmt(self.size),\
                                                   hsh=self.hashes['sha1'])

    @classmethod
    def from_trx(cls,trx):
        asset = cls()
        ct = trx.response.headers['Content-Type']
        if type(ct) == list and len(ct) > 0:
            ct = ct[0]
        if ct and type(ct) == str:
            ct = ct.split("/")
            asset.type = ct[0].strip()
            if len(ct) > 1:
                ct = ct[1].split(";")
                asset.subtype = ct[0].strip()
                if len(ct) > 1:
                    asset.argument = ct[1].split("=")
        # else:
        #     print("content-type: None - t:{}".format(type(ct)))
        
        asset.scheme = trx.request.scheme
        asset.host = trx.request.host
        asset.port = trx.request.port
        asset.path = trx.request.path

        asset.content = trx.response.content # usually 'str' form
        asset.size = len(asset.content)
        asset.start_time = trx.request.timestamp_start
        asset.end_time = trx.response.timestamp_end
        
        asset.hashes = {}
        algos = filter(lambda x: x in hashlib.algorithms,['md5','sha1','sha256'])
        for algo in algos:
            h = hashlib.new(algo)
            h.update(asset.content)
            asset.hashes[algo] = h.hexdigest()
        
        return asset
        
