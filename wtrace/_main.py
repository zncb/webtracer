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

""" A web transaction tracer using Selenium and mitmproxy. """

from wtrace.tracer import WebTracer
from wtrace.traces import TraceTarget,TraceDesc

def trace(args):
    import os
    if not args.json_targets and not args.inline_target:
        print("Please specify a url with -u or a target list with -t")
        exit(1)

    targets = []

    if args.json_targets:
        targets += list(reduce(lambda x,y:x+y,[TraceTarget.load_from_json_file(f) for f in args.json_targets]))
        
    if args.inline_target:
        targets.append(TraceTarget(args.inline_target[0],args.inline_target[1]))
        
    tracer = WebTracer()
    tracer.trace(targets)

    output_dir = os.path.abspath(args.trace_dir[0])
    tracer.serialize_traces_to_dir(output_dir)

def analyze(args):
    import os
    from wtrace.analysis import AnalysisRunner
    
    trace_dir = os.path.abspath(args.trace_dir[0])
    trace_file = None
    tracer = WebTracer()
        
    if args.trace_file:
        trace_file = os.path.abspath(args.trace_file[0])
        tracer.load_trace_from_file(trace_file)
    elif args.trace_dir:
        tracer.load_traces_from_dir(trace_dir)

    if args.list:
        tracer.list_traces()
        return 0

    scripts = args.analysis_scripts
    if not scripts or len(scripts) < 1:
        print('>> Nothing to do...')
        return 0
    scripts = [os.path.abspath(s) for s in scripts]

    runner = AnalysisRunner(tracer.traces)
    runner.run(scripts)


def main():
    import argparse,os,signal
    from functools import reduce
    from ._version import __version__

    def sigint(signum,frame):
        print('>> Caught sigint, bye!')
        sys.exit(0)

    signal.signal(signal.SIGINT,sigint)
    
    # top level parser
    parser = argparse.ArgumentParser(prog='wtrace',
                                     description='Trace http transactions and asset dependencies involved in loading a web page.',
                                     epilog='version: {}'.format(__version__))
    
    # sub-actions
    subparsers = parser.add_subparsers(help='action to perform')
    parser_trace = subparsers.add_parser('trace',help='perform tracing')
    parser_analyze = subparsers.add_parser('analyze',help='analyze traces')

    # setup trace args
    group = parser_trace.add_mutually_exclusive_group()
    group.add_argument('-j','--json-targets',nargs='+',type=str,
                        help='paths to trace target files (json)')
    group.add_argument('-i','--inline-target',nargs=2,type=str,
                        help='trace inline target: name url')

    parser_trace.add_argument('-d','--trace-dir',nargs=1,type=str,
                             default=[os.getcwd()],
                             help='path to trace directory')
    parser_trace.set_defaults(func=trace)

    # setup analyze args
    group = parser_analyze.add_mutually_exclusive_group()
    group.add_argument('-d','--trace-dir',nargs=1,type=str,
                        default=[os.getcwd()],
                        help='path to trace directory')
    group.add_argument('-f','--trace-file',nargs=1,type=str,
                       help='path to trace file')

    group = parser_analyze.add_mutually_exclusive_group()
    group.add_argument('-l','--list',action='store_true',help='list available traces')
    group.add_argument('-a','--analysis-scripts',nargs='+',help='custom analysis scripts')


    parser_analyze.set_defaults(func=analyze)
    
    # parse args and let control flow to proper funcs
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
