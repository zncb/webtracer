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

""" Trace harvester interface to mitmproxy. """

import cPickle,sys
from libmproxy import controller, proxy
from libmproxy.proxy.server import ProxyServer
from wtrace.httptrx import HTTPTrx

class HarvesterProxy(controller.Master):
    def __init__(self,host='localhost',port=8080,ssl_port=8383):
        self.pickler = cPickle.Pickler(sys.stdout,cPickle.HIGHEST_PROTOCOL)
        self.host = host
        self.port = port
        self.ssl_port = ssl_port
        self.config = proxy.ProxyConfig(host=host,port=port,ssl_ports=[443,ssl_port])
        self.server = ProxyServer(self.config)
        controller.Master.__init__(self,self.server)

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, flow):
        #hid = (flow.request.host, flow.request.port)
        flow.reply()

    def handle_response(self, flow):
        #hid = (flow.request.host, flow.request.port)
        #print("resp> {}".format(flow.response))
        self.pickler.dump(HTTPTrx(flow.request,flow.response))
        sys.stdout.flush()
        flow.reply()

    def address(self):
        return {'host': self.host, 'port': self.port, 'ssl_port': self.ssl_port}


def main():
    import argparse,os,signal,time,sys
    
    parser = argparse.ArgumentParser(prog="harvesterproxy",\
                                     description="Starts a mitm proxy to sniff HTTP traffic.")
    parser.add_argument('host',type=str,\
                        help='ip to listen on')
    parser.add_argument('port',type=int,\
                        help='port to listen on')
    parser.add_argument('ssl_port',type=int,\
                        help='ssl port to listen on')
    args = parser.parse_args()

    hproxy = HarvesterProxy(host=args.host,port=args.port,ssl_port=[443,args.ssl_port])

    def sigusr1(signum,frame):
        hproxy.shutdown()
        time.sleep(0.5)
        exit(0)

    signal.signal(signal.SIGUSR1,sigusr1)

    hproxy.run()


if __name__ == "__main__":
    main()
