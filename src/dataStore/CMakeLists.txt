#
# CMake configuration for PerfTrack data store scripts.
#
# This file manages pecompilation and installation of PerfTrack
# Python modules and scripts related to the PerfTrack data store.
#
# Author:  Heath Harrelson <heath.harrelson@gmail.com>
# Created: 2013-08-08
#

set(PERFTRACK_DATA_STORE_SCRIPTS
	ptdf_entry.py
)

set(PERFTRACK_DATA_STORE_MODULES
	lru_cache.py
	PTds.py
	ptdfParser.py
	ptPyDBAPI.py
)

PYTHON_INSTALL_ALL(${PERFTRACK_MODULE_DIR} ${PERFTRACK_DATA_STORE_MODULES})
PYTHON_INSTALL_ALL(bin ${PERFTRACK_DATA_STORE_SCRIPTS})
