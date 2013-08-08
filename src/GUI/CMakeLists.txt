project(perftrack_gui)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/CMake/Modules")

find_package(PythonLibs REQUIRED)
find_package(Qt4 COMPONENTS QtCore QtGui QtSql Qt3Support REQUIRED)

include(${QT_USE_FILE})

set(PERFTRACK_GUI_HDRS
	attributedialog.h
	remotehostextension.h
	execution_resource_extension.h
	db_connection_dialog.h
	selection_dialog.h
	selection_dialog_base.h
	selection_list_item.h
	resource_selector.h
	resource_selector_base.h
	data_access.h
	result_table_cursor.h
	dataset.h
	tg_barchart.h
	chart_viewer.h
	chart_viewer_base.h
	row_sort_table.h
	resource_type_and_name.h
	host_connection.h
	pt_main_window.h
	pt_main_window_base.h
	data_table.h
	data_filter_dialog.h
	data_filter_dialog_base.h
	filter_op.h
	filter_list_box_item.h
	file_options_dialog.h
	file_options_dialog_base.h
	plot_data_dialog.h
	plot_data_dialog_base.h
	column_data_dialog.h
	column_data_dialog_base.h
	static_check_list_item.h
	constraint_list_item.h
	two_d_table.h
	select_operator_dialog.h
	select_operator_dialog_base.h
	comb_perfRes_widget.h
	comb_perfRes_widget_base.h
	combine_perfReses_dialog.h
	combine_perfReses_dialog_base.h
	operator.h
	operator_python_module_conf.h
	perfResult.h)

set(PERFTRACK_GUI_SRCS
	main.cpp
	attributedialog.cpp
	remotehostextension.cpp
	execution_resource_extension.cpp
	db_connection_dialog.cpp
	selection_dialog.cpp
	selection_dialog_base.cpp
	selection_list_item.cpp
	resource_selector.cpp
	resource_selector_base.cpp
	data_access.cpp
	result_table_cursor.cpp
	chart_viewer.cpp
	chart_viewer_base.cpp
	row_sort_table.cpp
	dataset.cpp
	tg_barchart.cpp
	resource_type_and_name.cpp
	host_connection.cpp
	pt_main_window.cpp
	pt_main_window_base.cpp
	data_table.cpp
	data_filter_dialog.cpp
	data_filter_dialog_base.cpp
	filter_op.cpp
	file_options_dialog.cpp
	file_options_dialog_base.cpp
	plot_data_dialog.cpp
	plot_data_dialog_base.cpp
	column_data_dialog.cpp
	column_data_dialog_base.cpp
	select_operator_dialog.cpp
	select_operator_dialog_base.cpp
	comb_perfRes_widget.cpp
	comb_perfRes_widget_base.cpp
	combine_perfReses_dialog.cpp
	combine_perfReses_dialog_base.cpp
	operator.cpp
	perfResult.cpp)

set(PERFTRACK_GUI_UI
	attributedialog.ui
	combine_perfReses_dialog_base.ui
	data_filter_dialog_base.ui
	file_options_dialog_base.ui
	remotehostextension.ui
	select_operator_dialog_base.ui
	chart_viewer_base.ui
	comb_perfRes_widget_base.ui
	db_connection_dialog.ui
	plot_data_dialog_base.ui
	resource_selector_base.ui
	column_data_dialog_base.ui
	data_dialog_base.ui
	execution_resource_extension.ui
	pt_main_window_base.ui
	selection_dialog_base.ui)

set(PERFTRACK_PLUGINS
	.ptoperators
	baseOps.py
	operator_pt.py)

set(PERFTRACK_PLUGIN_DIR
	pertftrack-plugins)

QT4_WRAP_UI(perftrack_gui_ui ${PERFTRACK_GUI_UI})
QT4_AUTOMOC(${PERFTRACK_GUI_SRCS})

# generate the header file that configures plugin locations
configure_file (
    "${PROJECT_SOURCE_DIR}/operator_python_module_conf.h.in"
    "${PROJECT_BINARY_DIR}/operator_python_module_conf.h"
)

ADD_DEFINITIONS(-DUSE_FULL_RESOURCE_NAMES=true -DPTRESDELIM=\"|\")
include_directories(${CMAKE_SOURCE_DIR} ${PROJECT_BINARY_DIR} ${CMAKE_CURRENT_BINARY_DIR} ${PYTHON_INCLUDE_DIRS} ${PYTHON_INCLUDE_PATH})

add_executable(perftrack ${PERFTRACK_GUI_SRCS} ${perftrack_gui_ui})
target_link_libraries(perftrack ${QT_LIBRARIES} ${PYTHON_LIBRARIES})

# copy python plugins to the build directory
foreach(plugin ${PERFTRACK_PLUGINS})
	configure_file(${plugin} ${plugin} COPYONLY)
endforeach(plugin)

# for make install
install(TARGETS perftrack DESTINATION bin)
install(FILES ${PERFTRACK_PLUGINS} DESTINATION lib/${PERFTRACK_PLUGIN_DIR})

