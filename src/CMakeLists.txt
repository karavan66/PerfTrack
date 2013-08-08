cmake_minimum_required(VERSION 2.6)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/CMake/Modules")

project(perftrack)

# determine Python interpreter, library path, site-packages path
find_package(PythonLibrary REQUIRED)
set(PERFTRACK_MODULE_DIR "${PYTHON_SITE_PACKAGES_INSTALL_DIR}/perftrack" CACHE PATH "Directory where PerfTrack Python modules will be installed.")

# perftrack gui
include_directories(${PROJECT_SOURCE_DIR}/GUI)
add_subdirectory(GUI)

