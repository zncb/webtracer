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

""" Trace target and descriptors """


class TraceTarget:

    def __init__(self,name,url):
        from urlparse import urlsplit
        self.name = name.replace(' ','_')
        self.url = url
        url_split = urlsplit(url)
        self.scheme = url_split.scheme
        self.netloc = url_split.netloc
        self.path = url_split.path
        self.query = url_split.query
        self.fragment = url_split.fragment

    def __str__(self):
        return "{self.name}: '{self.url}'".format(self=self)

    @classmethod
    def from_dict(cls,dct):
        return cls(dct['name'],dct['url'])
    
    @classmethod
    def req_fields(cls):
        return ['name','url']

    @classmethod
    def load_from_json_file(cls,filepath):
        import json,os,collections
        from functools import reduce
        filepath = os.path.abspath(filepath)
        
        if not os.path.exists(filepath):
            print("err> '{}' does not exist.".format(filepath))
            return None
        elif not os.path.isfile(filepath):
            print("err> '{}' not a regular file".format(filepath))
            return None
        
        try:
            fp = open(filepath,'r');
        except OSError as e:
            print("err> error opening file '{}': {}".format(filepath,e))
            return None

        def as_trace_target(dct):
            if reduce(lambda x,y:x and y,[f in dct for f in TraceTarget.req_fields()]):
                return cls.from_dict(dct)
            return dct
        
        targets = json.load(fp,object_hook=as_trace_target)
        if not isinstance(targets,collections.Iterable):
            targets = [targets]

        fp.close()
        
        return list(filter(lambda t:isinstance(t,TraceTarget),targets))


from libmproxy.protocol.http import HTTPRequest, HTTPResponse
from wtrace.asset import Asset

class TraceDesc:

    HTTPREQUEST=0
    HTTPRESPONSE=1
    
    def __init__(self,target):
        from urlparse import urlsplit
        self.target = target
        self.init_time = 0
        self.end_time = 0
        self.bytes_up = 0
        self.bytes_down = 0
        self.requests = 0
        self.responses = 0
        self.driver = 'unknown'
        self.source = None
        self.transactions = []
        self.assets = []
        
    def __str__(self):
        from utils import sizeof_fmt
        bw_up = sizeof_fmt(self.bytes_up)
        bw_down = sizeof_fmt(self.bytes_down)
        return u"[{name}] {bw_up}↑{bw_down}↓ | {req}↑{resp}↓  in {time:.2}s | {url}".format(name=self.target.name,url=self.target.url,\
                                                                                           time=self.end_time-self.init_time,\
                                                                                           bw_up=bw_up,bw_down=bw_down,\
                                                                                           req=self.requests,resp=self.responses)

    def add_trx(self,trx):
        # trx is an HTTPTrx
        self.transactions.append(trx)
        if trx.request:
            self.requests += 1
            self.bytes_up += trx.request.size()
        if trx.response:
            self.responses += 1
            self.bytes_down += trx.response.size()

        asset = Asset.from_trx(trx)
        print(str(asset))
        self.assets.append(asset)

    
    
