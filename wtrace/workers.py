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

""" Requester and Harvester components """

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from wtrace.traces import TraceDesc

class Requester:
    def __init__(self,driver='chrome',proxy_addr=None):
        if not driver in Requester.drivers():
            print("err> invalid requester driver: {}",str(driver))
        self.driver_name = driver
        
        http_proxy = ":".join([proxy_addr['host'],str(proxy_addr['port'])])
        ssl_proxy = ":".join([proxy_addr['host'],str(proxy_addr['ssl_port'])])
        proxy = Proxy({
             'proxyType': ProxyType.MANUAL,
             'httpProxy': http_proxy,
             'sslProxy': ssl_proxy,
        })
        caps = webdriver.DesiredCapabilities.CHROME.copy()
        proxy.add_to_capabilities(caps)
        caps['applicationCacheEnabled'] = False
        caps['chromeOptions'] = {'prefs': {'profile.block_third_party_cookies':False}}
        self._desired_caps = caps

    def _trace_chrome(self,tracedesc):
        from time import time,sleep
        print('req> '+tracedesc.target.url)
        driver = webdriver.Chrome(desired_capabilities=self._desired_caps)
        driver.implicitly_wait(30)
        driver.delete_all_cookies()
        tracedesc.driver = 'chrome'
        tracedesc.init_time = time()
        driver.get(tracedesc.target.url)
        sleep(10)
        tracedesc.end_time = time()
        tracedesc.source = driver.page_source
        driver.delete_all_cookies()
        driver.quit()
        sleep(0.5)
        return True #todo: get some more info from the driver

    def _trace_firefox(self,scandesc):
        pass # todo: implement this

    def trace(self,tracedesc):
        if self.driver_name == 'firefox':
            return self._trace_firefox(tracedesc)
        else:
            return self._trace_chrome(tracedesc)

    @classmethod
    def drivers(cls):
        return ['chrome','firefox']


import os,signal,time,sys,subprocess,Queue,cPickle
from threading import Thread
from libmproxy.protocol.http import HTTPRequest

class Harvester(Thread):
    def __init__(self,host='localhost',port=8080,ssl_port=8383):
        Thread.__init__(self)

        self.host = host
        self.port = port
        self.ssl_port = ssl_port

        self._queue = Queue.Queue()
        self._stop_signaled = False
        self._proxy_proc = None
        self._cur_trace = None
        

    # called via start()
    def run(self):
        if self._proxy_proc:
            self.stop()
            
        self._proxy_proc = subprocess.Popen(['{}/harvesterproxy.py'.format(os.path.dirname(__file__)),str(self.host),str(self.port),str(self.ssl_port)],
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE)
        unpickler = cPickle.Unpickler(self._proxy_proc.stdout)
        try:
            while not self._stop_signaled:
                http_trx = unpickler.load()
                if self._cur_trace:
                    self._queue.put(http_trx)
        except EOFError as e:
            pass

        self._proxy_proc = None
        
        
    def stop(self):
        if self._cur_trace:
            self.end_trace()
        if self._proxy_proc:
            self._stop_signaled = True
            os.kill(self._proxy_proc.pid,signal.SIGUSR1)
            time.sleep(0.5)

    def proxy_address(self):
        return self.proxy.address()

    def start_trace(self,tracedesc):
        if self._cur_trace:
            self.end_trace()
        self._cur_trace = tracedesc
            
    def end_trace(self):
        if self._cur_trace:
            try:
                while True:
                    self._cur_trace.add_trx(self._queue.get(block=False))
            except Queue.Empty:
                pass
        self._cur_trace = None
    
    def proxy_address(self):
        return {'host': self.host, 'port': self.port, 'ssl_port': self.ssl_port}
