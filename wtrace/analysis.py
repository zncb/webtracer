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

""" Handling of custom analysis """        

import os,time

class AnalysisRunner:

    def __init__(self,traces=[]):
        self._traces = traces

    def _run_script(self,path):
        from types import FunctionType
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
          and len(getargspec(wtrace_analysis).args) == 1:
            wtrace_analysis(self._traces)
            return True
        return False

        
    def run(self,scripts=[]):
        for s in scripts:
            try:
                print('>> Running: {}'.format(s))
                t0 = time.time()
                res = self._run_script(s)
                t1 = time.time()
                if res:
                    print('>> Success')
                else:
                    print('>> Failure')
                print('>> in {}sec'.format(t1-t0))
            except KeyboardInterrupt:
                print('int> aborting current analysis...')
            except Exception as e:
                print('err> caught exception while running analysis: {}'.format(e))
        
