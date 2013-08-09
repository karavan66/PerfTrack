#
# CMake configuration for PerfTrack data collection scripts.
#
# This file manages pecompilation and installation of PerfTrack
# Python modules and scripts related to the PerfTrack data col-
# lection.
#
# Author:  Heath Harrelson <heath.harrelson@gmail.com>
# Created: 2013-08-08
#

set(PERFTRACK_DATA_COLLECTION_SCRIPTS
	Hardware.py
	PERIxmlGen.py
	PTdFgen.py
	parsePerf.py
	ptGo.py
	run_oprofile.py
	run/ptrun.py
	sys2machine.py
	systemScan.py
)

set(PERFTRACK_DATA_COLLECTION_MODULES
	Application.py
	AttrVal.py
	Build.py
	Execution.py
	ParseOprof.py
	PERIxml.py
	PerfResult.py
	PTcommon.py
	PTexception.py
	parseMilc.py
	parsePerf.py
	parsePurple.py
	Resource.py
	ResourceIndex.py
	Run.py
	toolParser.py
	machine/gm_hs_tools.py
	machine/gmLogger.py
	machine/iMDL.py
	machine/ptdf.py
	machine/pt_nwice_proc.py
	machine/pt_proc.py
	machine/pt_xt4_proc.py
	run/filesystem.py
	run/ptCNLfix.py
	run/submission.py
)

set(PERFTRACK_MISC_CONFIG_FILES
	machine/nwice.iMDL.cfg
	machine/ruby.iMDL.cfg
)

PYTHON_INSTALL_ALL(
	${PERFTRACK_MODULE_DIR}
	${PERFTRACK_DATA_COLLECTION_MODULES}
)

PYTHON_INSTALL_ALL(bin ${PERFTRACK_DATA_COLLECTION_SCRIPTS})

install(FILES ${PERFTRACK_MISC_CONFIG_FILES}
	DESTINATION ${PERFTRACK_MODULE_DIR}
)
