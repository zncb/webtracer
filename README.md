## wtrace

A simple tracer for web page assets using Selenium and libmproxy.

Note: This is very much a work in progress.

### Installation

Checkout the project, move to the project directory and run:

	$ sudo python ./setup.py install

Provided your paths are properly setup you should now be able to run wtrace


### Basic Usage

	$ wtrace -h
	usage: wtrace [-h] {trace,analyze} ...
	
	Trace http transactions and asset dependencies involved in loading a web page.
	
	positional arguments:
	{trace,analyze}  action to perform
		trace          perform tracing
		analyze        analyze traces

	optional arguments:
		-h, --help       show this help message and exit


### Tracing

	$ wtrace trace -h
	usage: wtrace trace [-h] [-j JSON_TARGETS [JSON_TARGETS ...] | -i
                    INLINE_TARGET INLINE_TARGET] [-d TRACE_DIR]
	
	optional arguments:
		-h, --help            show this help message and exit
		-j JSON_TARGETS [JSON_TARGETS ...], --json-targets JSON_TARGETS [JSON_TARGETS ...]
			                  paths to trace target files (json)
	-i INLINE_TARGET INLINE_TARGET, --inline-target INLINE_TARGET INLINE_TARGET
		                      trace inline target: name url
	-d TRACE_DIR, --trace-dir TRACE_DIR
		                      path to trace directory

### Analyzing

	$ wtrace analyze -h
	usage: wtrace analyze [-h] [-d TRACE_DIR | -f TRACE_FILE]
		                  [-l | -a ANALYSIS_SCRIPTS [ANALYSIS_SCRIPTS ...]]

	optional arguments:
		-h, --help            show this help message and exit
		-d TRACE_DIR, --trace-dir TRACE_DIR
			                  path to trace directory
	-f TRACE_FILE, --trace-file TRACE_FILE
                              path to trace file
	-l, --list                list available traces
	-a ANALYSIS_SCRIPTS [ANALYSIS_SCRIPTS ...], --analysis-scripts ANALYSIS_SCRIPTS [ANALYSIS_SCRIPTS ...]
                              custom analysis scripts

### Analysis Scripts

An analysis script is just a plain python script providing the following entry point:

	from wtrace.traces import *
	from wtrace.asset import *
	
	def wtrace_analysis(traces=[]):
		for t in traces:
			print('Do something')



The 'traces' array will contain instances of TraceDesc. For details use the help function in a Python repl:

	> from wtrace.traces import TraceDesc
	> help(TraceDesc)


