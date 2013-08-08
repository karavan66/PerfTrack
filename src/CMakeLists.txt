cmake_minimum_required(VERSION 2.6)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/CMake/Modules")

project(perftrack)

# determine Python interpreter, library path, site-packages path
find_package(PythonLibrary REQUIRED)

# perftrack gui
include_directories(${PROJECT_SOURCE_DIR}/GUI)
add_subdirectory(GUI)

