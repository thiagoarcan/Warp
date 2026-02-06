# Testes Automatizados PyQt6 - Platform Base

Suite completa de testes automatizados para a aplicação PyQt6 Platform Base.

## 📋 Visão Geral

Esta suite de testes cobre todos os aspectos críticos da aplicação sem necessidade de interação manual:

1. **Carregamento de arquivos .ui** - Valida que todos os 72 arquivos .ui podem ser carregados
2. **Validação de widgets obrigatórios** - Verifica widgets críticos em cada tela
3. **Navegação e inicialização** - Testa fluxos de navegação entre telas
4. **Sinais e slots** - Verifica conexões de sinais/slots
5. **Memory leaks** - Detecta vazamentos de memória
6. **Exceções e erros** - Valida tratamento de erros

## 🚀 Execução Rápida

### Executar todos os testes automatizados

```bash
# Com script sh (recomendado)
./tests/automated/run_automated_tests.sh

# Ou diretamente com pytest
pytest tests/automated/ -v -m gui
```

### Executar com cobertura de código

```bash
pytest tests/automated/ -v -m gui \
    --cov=platform_base \
    --cov-report=html \
    --cov-report=term-missing
```

### Executar testes específicos

```bash
# Apenas carregamento de .ui
pytest tests/automated/test_01_ui_files_loading.py -v

# Apenas validação de widgets
pytest tests/automated/test_02_widgets_validation.py -v

# Apenas memory leaks
pytest tests/automated/test_05_memory_leaks.py -v
```

## 📊 Relatórios Gerados

Após executar os testes, os seguintes relatórios são gerados:

- **`htmlcov_automated/index.html`** - Relatório HTML de cobertura
- **`coverage_automated.json`** - Dados de cobertura em JSON
- **`test_results_automated.xml`** - Resultados em formato JUnit XML

## 🔍 Estrutura dos Testes

### test_01_ui_files_loading.py

Valida carregamento de todos os arquivos .ui:

- ✅ Cada arquivo .ui pode ser carregado sem erros
- ✅ XML é válido e bem-formado
- ✅ Arquivos não estão vazios
- ✅ Recursos referenciados são válidos
- ✅ Conexões signal/slot estão corretas

### test_02_widgets_validation.py

Verifica widgets obrigatórios:

- ✅ MainWindow tem menu bar, status bar, central widget
- ✅ MainWindow tem dock widgets necessários
- ✅ Diálogos têm botões e labels apropriados
- ✅ Widgets têm object names quando necessário
- ✅ Estados iniciais são corretos

### test_03_navigation_and_initialization.py

Testa navegação e inicialização:

- ✅ Aplicação pode ser inicializada
- ✅ DatasetStore, SessionState, SignalHub podem ser criados
- ✅ MainWindow pode ser instanciado
- ✅ Todos os diálogos podem ser importados
- ✅ Todos os painéis podem ser importados
- ✅ UiLoaderMixin funciona corretamente

### test_04_signals_and_slots.py

Verifica sinais e slots:

- ✅ SignalHub tem sinais definidos
- ✅ Sinais podem ser conectados
- ✅ Sinais podem ser desconectados
- ✅ Múltiplas conexões funcionam
- ✅ Decorador @pyqtSlot funciona
- ✅ QTimer timeout sinal funciona

### test_05_memory_leaks.py

Detecta vazamentos de memória:

- ✅ Widgets são deletados corretamente
- ✅ Múltiplos widgets não causam leak
- ✅ Conexões de sinais não causam leak
- ✅ Memória permanece estável com criações repetidas
- ✅ Garbage collection funciona
- ✅ Referências circulares são tratadas

### test_06_exceptions_and_errors.py

Valida tratamento de erros:

- ✅ Arquivo .ui inválido gera erro apropriado
- ✅ MainWindow sem .ui gera RuntimeError
- ✅ Widget sobrevive a exceção em handler
- ✅ Múltiplos erros não crasham aplicação
- ✅ Entrada inválida é tratada
- ✅ Condições de contorno são verificadas

## 🎯 Marcadores de Teste

Os testes usam marcadores pytest para organização:

- `@pytest.mark.gui` - Testes que requerem Qt
- `@pytest.mark.slow` - Testes que demoram mais
- `@pytest.mark.parametrize` - Testes parametrizados

## 🔧 Configuração

### Requisitos

```bash
pip install -e ".[dev]"
```

Instala:
- pytest >= 7.3.0
- pytest-qt >= 4.3.0
- pytest-cov >= 4.1.0
- pytest-xdist >= 3.3.0
- psutil >= 5.9.0

### Variáveis de Ambiente

```bash
# Forçar offscreen rendering (automático nos testes)
export QT_QPA_PLATFORM=offscreen

# Desabilitar mensagens de debug do Qt
export QT_LOGGING_RULES="*.debug=false"
```

## 📈 Métricas de Qualidade

### Cobertura Esperada

- **Mínimo:** 60% de cobertura
- **Recomendado:** 80% de cobertura
- **Excelente:** 90%+ de cobertura

### Tempo de Execução

- Testes rápidos: ~30 segundos
- Testes completos: ~2-3 minutos
- Testes com memory leak: ~5 minutos

## 🐛 Troubleshooting

### Erro: "libEGL.so.1: cannot open shared object file"

**Solução:** Use offscreen platform:

```bash
export QT_QPA_PLATFORM=offscreen
pytest tests/automated/
```

### Erro: "No module named 'pytest'"

**Solução:** Instale dependências de desenvolvimento:

```bash
pip install -e ".[dev]"
```

### Testes lentos ou travando

**Solução:** Use xdist para paralelização:

```bash
pytest tests/automated/ -n auto
```

### Memory leak tests falhando

**Solução:** Aumente timeout ou pule testes lentos:

```bash
pytest tests/automated/ -m "gui and not slow"
```

## 🔄 Integração Contínua

### GitHub Actions

```yaml
- name: Run Automated Tests
  run: |
    export QT_QPA_PLATFORM=offscreen
    pytest tests/automated/ -v -m gui \
      --cov=platform_base \
      --cov-report=xml \
      --junit-xml=test-results.xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### GitLab CI

```yaml
test:automated:
  script:
    - export QT_QPA_PLATFORM=offscreen
    - pytest tests/automated/ -v -m gui --cov=platform_base
  artifacts:
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## 📚 Documentação Adicional

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

## ✅ Checklist de Validação

Antes de aprovar PR, verifique:

- [ ] Todos os testes passam
- [ ] Cobertura >= 60%
- [ ] Nenhum memory leak detectado
- [ ] Nenhuma exceção não tratada
- [ ] Relatórios gerados corretamente
- [ ] Documentação atualizada

## 🎓 Exemplos de Uso

### Adicionar novo teste de widget

```python
@pytest.mark.gui
def test_my_new_widget(self, qtbot):
    """Descrição do teste"""
    widget = MyWidget()
    qtbot.addWidget(widget)
    
    # Testes
    assert widget.isEnabled()
```

### Testar sinal/slot

```python
@pytest.mark.gui
def test_signal_emission(self, qtbot):
    """Testa emissão de sinal"""
    obj = MyObject()
    
    received = []
    obj.my_signal.connect(lambda: received.append(True))
    
    obj.my_signal.emit()
    
    assert len(received) > 0
```

### Testar memory leak

```python
@pytest.mark.gui
def test_no_leak(self, qtbot, clean_qapp):
    """Testa memory leak"""
    import gc
    
    widgets = [QWidget() for _ in range(100)]
    for w in widgets:
        qtbot.addWidget(w)
        w.deleteLater()
    
    qtbot.wait(100)
    gc.collect()
    
    # Verificar memória
```

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique a documentação acima
2. Consulte os exemplos de teste
3. Abra uma issue no repositório

---

**Última Atualização:** 2026-02-06  
**Versão:** 1.0.0  
**Mantido por:** Platform Base Team
