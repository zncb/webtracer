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

""" Wrapper for running analysis in seperate processes """

def run_analysis(path,traces=[]):
    import os
    from types import FunctionTypes
    from inspect import getargspec
    
    path = os.path.abspath(path)

    if not os.path.isfile(path):
        return False

    wtrace_analysis = None
    
    try:
        exec(open(path).read())
    except Error as e:
        return False

    if wtrace_analysis \
      and type(wtrace_analysis) is FunctionType \
      and (len(getargspec(wtrace_analysis)) == 1):
        wtrace_analysis(traces)
        return True
    return False

def main():
    import argparse,cPickle,os,signal,time,sys
    from wtrace.traces import TraceDesc
    
    parser = argparse.ArgumentParser(prog="analysisrunner",\
                                     description="Waits for pickled analysis instances on stdin and runs them.")
    args = parser.parse_args()

    cur_analysis = None

    def sigusr1(signum,frame):
        if cur_analysis:
            cur_analysis.shutdown()
        time.sleep(0.5)
        exit(0)

    signal.signal(signal.SIGUSR1,sigusr1)

    unpickler = cPickle.Unpickler(sys.stdin)

    traces = []
    
    try:
        while True:
            obj = unpickler.load()
            if obj:               
                if isinstance(obj,str):
                    run_analysis(obj,traces)
                elif isinstance(obj,TraceDesc):
                    traces.append(obj)
            time.sleep(0.01)
            
    except EOFError as e:
        print('err> runner got eof: {}'.format(e))
        

if __name__ == "__main__":
    main()
