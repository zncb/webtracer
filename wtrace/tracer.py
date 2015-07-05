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

""" Trace http transactions and asset dependencies involved in loading a web page """

from wtrace.workers import Requester,Harvester
from wtrace.traces import TraceTarget,TraceDesc

class WebTracer:
    def __init__(self):
        self.traces = []
    
    def trace(self,target_list):
        harvester = Harvester()
        harvester.start() # launch proxy process and monit thread
        requester = Requester(proxy_addr=harvester.proxy_address())
        tracedescs = []
        for target in target_list:
            tracedesc = TraceDesc(target)
            harvester.start_trace(tracedesc)
            requester.trace(tracedesc)
            harvester.end_trace()
            tracedescs.append(tracedesc)
        harvester.stop()
        self.traces += tracedescs
        return tracedescs

    def serialize_traces_to_dir(self,path):
        import cPickle, os
        for t in self.traces:
            try:
                fp = open(os.path.join(path,t.target.name+'.wt'),'w+')
                cPickle.dump(t,fp,cPickle.HIGHEST_PROTOCOL)
                fp.close()
            except OSError as e:
                print('err> error serializing trace: {}\n'.format(e))

    def load_trace_from_file(self,path):
        import cPickle, os
        try:
            fp = open(path,'r')
            t = cPickle.load(fp)
            fp.close()
            if isinstance(t,TraceDesc):
                self.traces.append(t)
            else:
                print(u'discarding invalid trace {}\n'.format(unicode(t)))
        except OSError as e:
            print('err> error loading trace: {}\n'.format(e))

    def load_traces_from_dir(self,path):
        import cPickle, os, glob
        files = glob.glob(os.path.join(path,'*.wt'))
        for fp in files:
            self.load_trace_from_file(fp)
            
    def list_traces(self):
        print(u"\n".join(unicode(t) for t in self.traces))


