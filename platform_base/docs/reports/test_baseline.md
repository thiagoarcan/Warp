# Test Baseline

Generated at: 2026-04-04T00:54:31
Command: C:\ProgramData\anaconda3\python.exe -m pytest tests/automated --html=C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base\docs\reports\test_report.html --self-contained-html --junitxml=C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base\docs\reports\junit.xml -q
Working directory: C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base
QT_QPA_PLATFORM=offscreen
PYTHONPATH=src
Exit code: 0
Pytest summary: =========== 202 passed, 29 skipped, 3 warnings in 340.07s (0:05:40) ===========

## Stdout (last 80 lines)
```text
PyQt6 6.7.1 -- Qt runtime 6.7.3 -- Qt compiled 6.7.1
rootdir: C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base
configfile: pyproject.toml
plugins: anyio-4.2.0, dash-3.3.0, hypothesis-6.151.4, asyncio-1.2.0, benchmark-5.2.3, cov-7.0.0, html-4.2.0, metadata-3.1.1, mock-3.15.1, mpl-0.18.0, qt-4.5.0, timeout-2.4.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 231 items

tests\automated\test_01_ui_loading.py ..............                     [  6%]
tests\automated\test_02_mandatory_widgets.py .......................     [ 16%]
tests\automated\test_03_navigation.py ....s..s........ss..s..sssss..     [ 29%]
tests\automated\test_04_signals_slots.py ...............                 [ 35%]
tests\automated\test_05_initialization.py ...............ss...s........s [ 48%]
sssss                                                                    [ 50%]
tests\automated\test_06_resources.py .........s...ssssss......           [ 61%]
tests\automated\test_07_state_visibility.py ...........................  [ 73%]
tests\automated\test_08_memory_leaks.py ................                 [ 80%]
tests\automated\test_09_exceptions_errors.py ..........s.s............   [ 90%]
tests\automated\test_10_coverage.py ..........s..........                [100%]

============================== warnings summary ===============================
tests/automated/test_09_exceptions_errors.py::TestMalformedDataHandling::test_inf_in_dataframe
  C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Warp\platform_base\tests\automated\test_09_exceptions_errors.py:107: FutureWarning: ChainedAssignmentError: behaviour will change in pandas 3.0!
  You are setting values through chained assignment. Currently this works in certain cases, but when using Copy-on-Write (which will become the default behaviour in pandas 3.0) this will never work to update the original DataFrame or Series, because the intermediate object on which we are setting values will behave as a copy.
  A typical example is when you are setting values in a column of a DataFrame, like:
  
  df["col"][row_indexer] = value
  
  Use `df.loc[row_indexer, "col"] = values` instead, to perform the assignment in a single step and ensure this keeps updating the original `df`.
  
  See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

tests/automated/test_09_exceptions_errors.py::TestMalformedDataHandling::test_inf_in_dataframe
  C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Warp\platform_base\tests\automated\test_09_exceptions_errors.py:108: FutureWarning: ChainedAssignmentError: behaviour will change in pandas 3.0!
  You are setting values through chained assignment. Currently this works in certain cases, but when using Copy-on-Write (which will become the default behaviour in pandas 3.0) this will never work to update the original DataFrame or Series, because the intermediate object on which we are setting values will behave as a copy.
  A typical example is when you are setting values in a column of a DataFrame, like:
  
  df["col"][row_indexer] = value
  
  Use `df.loc[row_indexer, "col"] = values` instead, to perform the assignment in a single step and ensure this keeps updating the original `df`.
  
  See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

tests/automated/test_09_exceptions_errors.py::TestMalformedDataHandling::test_inf_in_dataframe
  C:\ProgramData\anaconda3\Lib\site-packages\numpy\core\_methods.py:49: RuntimeWarning: invalid value encountered in reduce
    return umr_sum(a, axis, dtype, out, keepdims, initial, where)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
- generated xml file: C:\Users\tdyb\OneDrive - TRANSPETRO\Área de Trabalho\Projetos em Python\Warp\platform_base\docs\reports\junit.xml -
- Generated html report: file:///C:/Users/tdyb/OneDrive%20-%20TRANSPETRO/%C3%81rea%20de%20Trabalho/Projetos%20em%20Python/Warp/platform_base/docs/reports/test_report.html -
=========================== short test summary info ===========================
SKIPPED [1] tests\automated\test_03_navigation.py:150: Menus encontrados: ['ðÿ“\x81 arquivo', 'âœ\x8fï¸\x8f editar', 'ðÿ‘\x81ï¸\x8f visualizar', 'ðÿž¨ temas', 'ðÿ”§ ferramentas', 'â\x9d“ ajuda']
SKIPPED [1] tests\automated\test_03_navigation.py:203: NÃ£o foi possÃ­vel instanciar SettingsDialog: SettingsDialog.__init__() missing 1 required positional argument: 'session_state'
SKIPPED [1] tests\automated\test_03_navigation.py:257: NÃ£o foi possÃ­vel instanciar ConfigPanel: 'ConfigPanel' object has no attribute '_theme_combo'
SKIPPED [1] tests\automated\test_03_navigation.py:257: NÃ£o foi possÃ­vel instanciar OperationsPanel: OperationsPanel.__init__() got an unexpected keyword argument 'parent'
SKIPPED [1] tests\automated\test_03_navigation.py:272: ConfigPanel nÃ£o disponÃ­vel
SKIPPED [1] tests\automated\test_03_navigation.py:376: Tema light nÃ£o pÃ´de ser aplicado: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] tests\automated\test_03_navigation.py:376: Tema dark nÃ£o pÃ´de ser aplicado: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] tests\automated\test_03_navigation.py:376: Tema ocean nÃ£o pÃ´de ser aplicado: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] tests\automated\test_03_navigation.py:376: Tema forest nÃ£o pÃ´de ser aplicado: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] tests\automated\test_03_navigation.py:376: Tema sunset nÃ£o pÃ´de ser aplicado: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] tests\automated\test_05_initialization.py:190: NÃ£o foi possÃ­vel criar ConfigPanel: 'ConfigPanel' object has no attribute '_theme_combo'
SKIPPED [1] tests\automated\test_05_initialization.py:190: NÃ£o foi possÃ­vel criar OperationsPanel: OperationsPanel.__init__() got an unexpected keyword argument 'parent'
SKIPPED [1] tests\automated\test_05_initialization.py:233: NÃ£o foi possÃ­vel criar SettingsDialog: SettingsDialog.__init__() missing 1 required positional argument: 'session_state'
SKIPPED [1] tests\automated\test_05_initialization.py:283: ConfigManager nÃ£o disponÃ­vel
SKIPPED [1] tests\automated\test_05_initialization.py:290: ConfigManager nÃ£o disponÃ­vel
SKIPPED [1] tests\automated\test_05_initialization.py:308: UndoManager nÃ£o disponÃ­vel
SKIPPED [1] tests\automated\test_05_initialization.py:315: UndoManager nÃ£o disponÃ­vel
SKIPPED [1] tests\automated\test_05_initialization.py:325: UndoManager nÃ£o disponÃ­vel
SKIPPED [1] tests\automated\test_05_initialization.py:357: ConfigPanel requer arquivo .ui
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_06_resources.py:118: Nenhum CSV de exemplo encontrado
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_06_resources.py:201: Erro ao aplicar tema light: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_06_resources.py:201: Erro ao aplicar tema dark: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_06_resources.py:201: Erro ao aplicar tema ocean: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_06_resources.py:201: Erro ao aplicar tema forest: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_06_resources.py:201: Erro ao aplicar tema sunset: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_06_resources.py:217: Erro ao aplicar tema default: 'ThemeManager' object has no attribute 'apply_theme'
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_09_exceptions_errors.py:205: Handler de exceção não disponível
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_09_exceptions_errors.py:250: BaseWorker não disponível
SKIPPED [1] ..\..\..\Warp\platform_base\tests\automated\test_10_coverage.py:243: Módulo panels não disponível
=========== 202 passed, 29 skipped, 3 warnings in 340.07s (0:05:40) ===========
```

## Stderr (last 40 lines)
```text
(none)
```
