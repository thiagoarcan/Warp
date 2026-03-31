# Test Baseline

Generated at: 2026-03-31T12:52:58
Command: C:\ProgramData\anaconda3\python.exe -m pytest tests/automated --html=C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base\docs\reports\test_report.html --self-contained-html --junitxml=C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base\docs\reports\junit.xml -v
Working directory: C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base
QT_QPA_PLATFORM=offscreen
PYTHONPATH=src
Exit code: 3221225477
Pytest summary: tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[shortcutsDialog.ui] PASSED [ 16%]

## Stdout (last 80 lines)
```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-8.4.2, pluggy-1.6.0 -- C:\ProgramData\anaconda3\python.exe
cachedir: .pytest_cache
hypothesis profile 'default'
benchmark: 5.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
metadata: {'Python': '3.12.4', 'Platform': 'Windows-11-10.0.26100-SP0', 'Packages': {'pytest': '8.4.2', 'pluggy': '1.6.0'}, 'Plugins': {'anyio': '4.2.0', 'dash': '3.3.0', 'hypothesis': '6.151.4', 'asyncio': '1.2.0', 'benchmark': '5.2.3', 'cov': '7.0.0', 'html': '4.2.0', 'metadata': '3.1.1', 'mock': '3.15.1', 'mpl': '0.18.0', 'qt': '4.5.0', 'timeout': '2.4.0', 'xdist': '3.8.0'}}
Matplotlib: 3.10.5
Freetype: 2.6.1
PyQt6 6.7.1 -- Qt runtime 6.7.3 -- Qt compiled 6.7.1
rootdir: C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base
configfile: pyproject.toml
plugins: anyio-4.2.0, dash-3.3.0, hypothesis-6.151.4, asyncio-1.2.0, benchmark-5.2.3, cov-7.0.0, html-4.2.0, metadata-3.1.1, mock-3.15.1, mpl-0.18.0, qt-4.5.0, timeout-2.4.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 231 items

tests/automated/test_01_ui_loading.py::TestUIFilesExistence::test_ui_files_dir_exists <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  0%]
tests/automated/test_01_ui_loading.py::TestUIFilesExistence::test_ui_files_not_empty <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  0%]
tests/automated/test_01_ui_loading.py::TestUIFilesExistence::test_minimum_ui_files_count <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  1%]
tests/automated/test_01_ui_loading.py::TestUIFilesExistence::test_expected_core_ui_files_exist <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  1%]
tests/automated/test_01_ui_loading.py::TestUIXmlValidity::test_all_ui_files_are_valid_xml <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  2%]
tests/automated/test_01_ui_loading.py::TestUIXmlValidity::test_ui_xml_valid_batch <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  2%]
tests/automated/test_01_ui_loading.py::TestUIXmlStructure::test_ui_has_root_widget <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  3%]
tests/automated/test_01_ui_loading.py::TestUIXmlStructure::test_ui_widget_count_reasonable <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  3%]
tests/automated/test_01_ui_loading.py::TestUILoadingWithPyQt::test_ui_loadable_with_uic_batch <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  3%]
tests/automated/test_01_ui_loading.py::TestUILoadingWithPyQt::test_core_ui_files_loadable <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  4%]
tests/automated/test_01_ui_loading.py::TestUICompiledFiles::test_compiled_files_exist_for_core_ui <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  4%]
tests/automated/test_01_ui_loading.py::TestUICompiledFiles::test_all_compiled_files_importable <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  5%]
tests/automated/test_01_ui_loading.py::TestUIFileNamingConventions::test_ui_filenames_lowercase_or_camelcase <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  5%]
tests/automated/test_01_ui_loading.py::TestUIFileNamingConventions::test_ui_widget_names_unique_in_file <- ..\..\..\Warp\platform_base\tests\automated\test_01_ui_loading.py PASSED [  6%]
tests/automated/test_02_mandatory_widgets.py::TestMandatoryWidgetsPresent::test_all_ui_files_have_root_widget PASSED [  6%]
tests/automated/test_02_mandatory_widgets.py::TestMandatoryWidgetsPresent::test_dialog_files_have_dialog_root PASSED [  6%]
tests/automated/test_02_mandatory_widgets.py::TestMandatoryWidgetsPresent::test_panel_files_have_widget_root PASSED [  7%]
tests/automated/test_02_mandatory_widgets.py::TestWidgetTypesCorrect::test_buttons_are_pushbuttons PASSED [  7%]
tests/automated/test_02_mandatory_widgets.py::TestWidgetTypesCorrect::test_views_are_view_types PASSED [  8%]
tests/automated/test_02_mandatory_widgets.py::TestWidgetNamesUnique::test_no_duplicate_object_names PASSED [  8%]
tests/automated/test_02_mandatory_widgets.py::TestLayoutsNotEmpty::test_main_layouts_have_children PASSED [  9%]
tests/automated/test_02_mandatory_widgets.py::TestMandatoryWidgetsInPanels::test_data_panel_has_data_view PASSED [  9%]
tests/automated/test_02_mandatory_widgets.py::TestMandatoryWidgetsInPanels::test_dialog_has_buttons PASSED [  9%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[modernMainWindow.ui] PASSED [ 10%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[dataPanel.ui] PASSED [ 10%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[vizPanel.ui] PASSED [ 11%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[operationsPanel.ui] PASSED [ 11%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[configPanel.ui] PASSED [ 12%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[resultsPanel.ui] PASSED [ 12%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[streamingControls.ui] PASSED [ 12%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[uploadDialog.ui] PASSED [ 13%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[settingsDialog.ui] PASSED [ 13%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[aboutDialog.ui] PASSED [ 14%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[exportDialog.ui] PASSED [ 14%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[filterDialog.ui] PASSED [ 15%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[smoothingDialog.ui] PASSED [ 15%]
tests/automated/test_02_mandatory_widgets.py::TestSpecificMandatoryWidgets::test_mandatory_widgets_from_config[shortcutsDialog.ui] PASSED [ 16%]
tests/automated/test_03_navigation.py::TestMainWindowDockPanels::test_main_window_instantiates <- ..\..\..\Warp\platform_base\tests\automated\test_03_navigation.py
```

## Stderr (last 40 lines)
```text
Windows fatal exception: access violation

Current thread 0x00008524 (most recent call first):
  File "C:\Users\tdyb\OneDrive - TRANSPETRO\\xc1rea de Trabalho\Projetos em Python\Warp\platform_base\src\platform_base\ui\main_window_unified.py", line 1599 in _organize_dock_layout
  File "C:\Users\tdyb\OneDrive - TRANSPETRO\\xc1rea de Trabalho\Projetos em Python\Warp\platform_base\src\platform_base\ui\main_window_unified.py", line 1560 in _restore_layout
  File "C:\Users\tdyb\OneDrive - TRANSPETRO\\xc1rea de Trabalho\Projetos em Python\Warp\platform_base\src\platform_base\ui\main_window_unified.py", line 158 in __init__
  File "C:\Users\tdyb\OneDrive - TRANSPETRO\\xc1rea de Trabalho\Warp\platform_base\tests\automated\test_03_navigation.py", line 64 in test_main_window_instantiates
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\python.py", line 157 in pytest_pyfunc_call
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_callers.py", line 121 in _multicall
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_manager.py", line 120 in _hookexec
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_hooks.py", line 512 in __call__
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\python.py", line 1671 in runtest
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\runner.py", line 178 in pytest_runtest_call
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_callers.py", line 121 in _multicall
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_manager.py", line 120 in _hookexec
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_hooks.py", line 512 in __call__
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\runner.py", line 246 in <lambda>
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\runner.py", line 344 in from_call
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\runner.py", line 245 in call_and_report
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\runner.py", line 136 in runtestprotocol
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\runner.py", line 117 in pytest_runtest_protocol
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_callers.py", line 121 in _multicall
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_manager.py", line 120 in _hookexec
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_hooks.py", line 512 in __call__
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\main.py", line 367 in pytest_runtestloop
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_callers.py", line 121 in _multicall
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_manager.py", line 120 in _hookexec
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_hooks.py", line 512 in __call__
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\main.py", line 343 in _main
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\main.py", line 289 in wrap_session
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\main.py", line 336 in pytest_cmdline_main
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_callers.py", line 121 in _multicall
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_manager.py", line 120 in _hookexec
  File "C:\ProgramData\anaconda3\Lib\site-packages\pluggy\_hooks.py", line 512 in __call__
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\config\__init__.py", line 175 in main
  File "C:\ProgramData\anaconda3\Lib\site-packages\_pytest\config\__init__.py", line 201 in console_main
  File "C:\ProgramData\anaconda3\Lib\site-packages\pytest\__main__.py", line 9 in <module>
  File "<frozen runpy>", line 88 in _run_code
  File "<frozen runpy>", line 198 in _run_module_as_main
```
