# Quick Reference - Testes Automatizados

## 🚀 Comandos Essenciais

### Executar Todos os Testes
```bash
pytest tests/automated/ -v -m gui
```

### Com Cobertura
```bash
pytest tests/automated/ -v -m gui --cov=platform_base --cov-report=html
```

### Script Completo
```bash
./tests/automated/run_automated_tests.sh
```

## 📊 Testes Disponíveis

| Arquivo | Descrição | Testes |
|---------|-----------|--------|
| `test_01_ui_files_loading.py` | Carregamento de .ui files | ~150 |
| `test_02_widgets_validation.py` | Validação de widgets | ~20 |
| `test_03_navigation_and_initialization.py` | Navegação/Init | ~15 |
| `test_04_signals_and_slots.py` | Sinais e slots | ~15 |
| `test_05_memory_leaks.py` | Memory leaks | ~12 |
| `test_06_exceptions_and_errors.py` | Erros/Exceções | ~18 |

**Total: ~230 testes automatizados**

## 🎯 Execução Seletiva

```bash
# Apenas carregamento de UI
pytest tests/automated/test_01_ui_files_loading.py -v

# Sem testes lentos
pytest tests/automated/ -m "gui and not slow"

# Apenas um teste específico
pytest tests/automated/test_01_ui_files_loading.py::TestUIFilesLoading::test_ui_file_loads_successfully -v

# Paralelo (mais rápido)
pytest tests/automated/ -n auto -m gui
```

## 📈 Interpretando Resultados

### Cobertura
- **90%+** = Excelente ✅
- **80-89%** = Bom ✓
- **60-79%** = Aceitável ⚠️
- **<60%** = Insuficiente ❌

### Memory Leaks
- **0 leaks** = Ideal ✅
- **<10MB growth** = Aceitável ⚠️
- **>50MB growth** = Problema ❌

## 🔧 Troubleshooting Rápido

```bash
# Erro de display
export QT_QPA_PLATFORM=offscreen

# Testes travando
pytest tests/automated/ --timeout=30

# Ver output completo
pytest tests/automated/ -vv --tb=long

# Depuração interativa
pytest tests/automated/ --pdb
```

## 📦 Relatórios

Após executar:
- `htmlcov_automated/index.html` - Cobertura visual
- `coverage_automated.json` - Dados JSON
- `test_results_automated.xml` - JUnit XML

## ✅ Checklist PR

- [ ] `pytest tests/automated/ -v` passa
- [ ] Cobertura >= 60%
- [ ] Sem memory leaks
- [ ] README atualizado

## 🎓 Exemplos Rápidos

### Testar Widget
```python
@pytest.mark.gui
def test_widget(qtbot):
    w = QWidget()
    qtbot.addWidget(w)
    assert w.isEnabled()
```

### Testar Sinal
```python
@pytest.mark.gui
def test_signal(qtbot):
    obj = MyObject()
    received = []
    obj.signal.connect(lambda: received.append(True))
    obj.signal.emit()
    assert len(received) > 0
```

### Testar Memory
```python
@pytest.mark.gui
def test_memory(qtbot, clean_qapp):
    import gc
    for _ in range(100):
        w = QWidget()
        qtbot.addWidget(w)
        w.deleteLater()
    qtbot.wait(100)
    gc.collect()
```

---

**Mais detalhes:** Ver `README.md` completo
