#!/usr/bin/env bash
# Script para executar testes automatizados com cobertura

set -e

echo "=========================================="
echo "Testes Automatizados PyQt6 - Platform Base"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Verificar se pytest está instalado
if ! python -m pytest --version &> /dev/null; then
    echo -e "${RED}pytest não está instalado. Instale com: pip install -e '.[dev]'${NC}"
    exit 1
fi

echo -e "${GREEN}1. Executando testes de carregamento de .ui files...${NC}"
python -m pytest tests/automated/test_01_ui_files_loading.py -v --tb=short -m gui || true

echo ""
echo -e "${GREEN}2. Executando testes de validação de widgets...${NC}"
python -m pytest tests/automated/test_02_widgets_validation.py -v --tb=short -m gui || true

echo ""
echo -e "${GREEN}3. Executando testes de navegação e inicialização...${NC}"
python -m pytest tests/automated/test_03_navigation_and_initialization.py -v --tb=short -m gui || true

echo ""
echo -e "${GREEN}4. Executando testes de sinais e slots...${NC}"
python -m pytest tests/automated/test_04_signals_and_slots.py -v --tb=short -m gui || true

echo ""
echo -e "${GREEN}5. Executando testes de memory leaks...${NC}"
python -m pytest tests/automated/test_05_memory_leaks.py -v --tb=short -m gui || true

echo ""
echo -e "${GREEN}6. Executando testes de exceções e erros...${NC}"
python -m pytest tests/automated/test_06_exceptions_and_errors.py -v --tb=short -m gui || true

echo ""
echo -e "${YELLOW}=========================================="
echo "Executando TODOS os testes automatizados com cobertura"
echo -e "==========================================${NC}"
echo ""

# Executar todos os testes com cobertura
python -m pytest tests/automated/ \
    -v \
    --tb=short \
    -m gui \
    --cov=platform_base \
    --cov-report=html:htmlcov_automated \
    --cov-report=term-missing \
    --cov-report=json:coverage_automated.json \
    --junit-xml=test_results_automated.xml || true

echo ""
echo -e "${GREEN}=========================================="
echo "Relatórios gerados:"
echo "  - HTML: htmlcov_automated/index.html"
echo "  - JSON: coverage_automated.json"
echo "  - JUnit XML: test_results_automated.xml"
echo -e "==========================================${NC}"
echo ""

# Mostrar resumo de cobertura
if [ -f "coverage_automated.json" ]; then
    echo -e "${YELLOW}Resumo de Cobertura:${NC}"
    python -c "
import json
with open('coverage_automated.json', 'r') as f:
    data = json.load(f)
    percent = data['totals']['percent_covered']
    print(f'  Cobertura Total: {percent:.2f}%')
    if percent >= 80:
        print('  Status: ✓ Excelente')
    elif percent >= 60:
        print('  Status: ✓ Bom')
    elif percent >= 40:
        print('  Status: ⚠ Precisa melhorar')
    else:
        print('  Status: ✗ Insuficiente')
    " || true
fi

echo ""
echo -e "${GREEN}Testes automatizados concluídos!${NC}"
