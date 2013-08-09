#
# CMakeLists.txt: Top-level CMake configuration for PerfTrack
#
project(perftrack)

cmake_minimum_required(VERSION 2.6)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/CMake/Modules")
include(PythonMacros)


# determine Python interpreter, library path, site-packages path
find_package(PythonLibrary REQUIRED)
set(PERFTRACK_MODULE_DIR "${PYTHON_SITE_PACKAGES_INSTALL_DIR}/perftrack" CACHE PATH "Directory where PerfTrack Python modules will be installed.")

# perftrack gui
message("== Configuring PerfTrack GUI ==")
include_directories(${PROJECT_SOURCE_DIR}/GUI)
add_subdirectory(GUI)

# perftrack data store python scripts
message("== Configuring PerfTrack Data Store Scripts ==")
add_subdirectory(dataStore)

# perftrack data collection python scripts
message("== Configuring PerfTrack Data Collection Scripts ==")
add_subdirectory(data_collection)
