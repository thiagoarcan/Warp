#!/usr/bin/env python
"""
Script para conectar classes Python aos arquivos .ui

Este script modifica as classes Python para:
1. Herdar de UiLoaderMixin
2. Carregar o arquivo .ui correspondente
3. Conectar os widgets aos signals

Fase 2 - Migração completa para Qt Designer
"""

from pathlib import Path


# Diretório base
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src" / "platform_base"
UI_DIR = SRC_DIR / "desktop" / "ui_files"

# Mapeamento de classes Python para arquivos .ui
CLASS_TO_UI_MAP = {
    # Painéis principais
    "desktop/widgets/data_panel.py:DataPanel": "dataPanel.ui",
    "desktop/widgets/viz_panel.py:VizPanel": "vizPanel.ui",
    "desktop/widgets/config_panel.py:ConfigPanel": "configPanel.ui",
    "desktop/widgets/results_panel.py:ResultsPanel": "resultsPanel.ui",

    # Diálogos principais
    "desktop/dialogs/upload_dialog.py:UploadDialog": "uploadDialog.ui",
    "desktop/dialogs/settings_dialog.py:SettingsDialog": "settingsDialog.ui",
    "desktop/dialogs/about_dialog.py:AboutDialog": "aboutDialog.ui",
    "desktop/dialogs/export_dialog.py:ExportDialog": "exportDialog.ui",

    # Painéis secundários
    "ui/panels/operations_panel.py:OperationsPanel": "operationsPanel.ui",
    "ui/panels/streaming_panel.py:StreamingPanel": "streamingPanel.ui",
    "ui/panels/performance_panel.py:PerformancePanel": "performancePanel.ui",
}

def get_ui_file_path(ui_filename: str) -> Path:
    """Retorna o caminho completo do arquivo .ui"""
    return UI_DIR / ui_filename


def check_ui_files_exist():
    """Verifica se todos os arquivos .ui necessários existem"""
    print("\n📋 Verificando arquivos .ui...")

    missing = []
    for ui_file in CLASS_TO_UI_MAP.values():
        ui_path = get_ui_file_path(ui_file)
        if ui_path.exists():
            print(f"  ✅ {ui_file}")
        else:
            print(f"  ❌ {ui_file} (FALTANDO)")
            missing.append(ui_file)

    return len(missing) == 0


def check_python_classes():
    """Verifica estado atual das classes Python"""
    print("\n📋 Verificando classes Python...")

    results = {
        "connected": [],
        "not_connected": [],
        "not_found": [],
    }

    for class_path, ui_file in CLASS_TO_UI_MAP.items():
        file_path, class_name = class_path.split(":")
        full_path = SRC_DIR / file_path

        if not full_path.exists():
            results["not_found"].append((file_path, class_name))
            print(f"  ❓ {class_name} - Arquivo não encontrado")
            continue

        content = full_path.read_text(encoding="utf-8")

        # Verificar se já usa UiLoaderMixin
        uses_mixin = "UiLoaderMixin" in content
        has_load_ui = "load_ui(" in content or "_load_ui(" in content

        if uses_mixin and has_load_ui:
            results["connected"].append((file_path, class_name))
            print(f"  ✅ {class_name} - Já conectado")
        else:
            results["not_connected"].append((file_path, class_name, ui_file))
            print(f"  ⚠️ {class_name} - Precisa conectar")

    return results


def generate_migration_instructions():
    """Gera instruções detalhadas de migração para cada classe"""

    print("\n" + "=" * 70)
    print("📝 INSTRUÇÕES DE MIGRAÇÃO PARA CADA CLASSE")
    print("=" * 70)

    for class_path, ui_file in CLASS_TO_UI_MAP.items():
        file_path, class_name = class_path.split(":")

        print(f"\n{'─' * 50}")
        print(f"📄 {class_name} ({file_path})")
        print(f"   UI: {ui_file}")
        print(f"{'─' * 50}")

        print(f"""
Modificações necessárias:

1. ADICIONAR IMPORT:
   from platform_base.ui.ui_loader_mixin import UiLoaderMixin

2. MODIFICAR HERANÇA:
   class {class_name}(QWidget, UiLoaderMixin):  # ou QDialog, UiLoaderMixin

3. ADICIONAR CONSTANTE:
   UI_FILE = "desktop/ui_files/{ui_file}"

4. NO __init__, ADICIONAR:
   # Logo após super().__init__(parent)
   self.load_ui(self.UI_FILE)

5. MODIFICAR _setup_ui():
   # Remover criação de widgets que já estão no .ui
   # Manter apenas conexões de signals e configurações dinâmicas

   def _setup_ui(self):
       # Os widgets já foram criados pelo load_ui()
       # Apenas configurar comportamento e conectar signals

       # Acessar widgets pelo nome definido no .ui
       self.my_button = self.findChild(QPushButton, "myButton")
       if self.my_button:
           self.my_button.clicked.connect(self._on_button_clicked)
""")


def create_sample_migrated_class():
    """Cria exemplo de classe migrada"""

    sample = '''"""
Exemplo de classe migrada para usar arquivo .ui

Este é um template de como uma classe deve ficar após a migração.
"""

from PyQt6.QtWidgets import QWidget, QPushButton
from platform_base.ui.ui_loader_mixin import UiLoaderMixin


class MigratedWidget(QWidget, UiLoaderMixin):
    """Widget que carrega interface de arquivo .ui"""

    # Caminho do arquivo .ui relativo à raiz do pacote
    UI_FILE = "desktop/ui_files/migratedWidget.ui"

    def __init__(self, parent=None):
        super().__init__(parent)

        # Carregar interface do arquivo .ui
        self.load_ui(self.UI_FILE)

        # Configurar widgets e conectar signals
        self._setup_widgets()
        self._connect_signals()

    def _setup_widgets(self):
        """Configura widgets carregados do .ui"""
        # Os widgets são acessados pelo objectName definido no Qt Designer
        # Exemplo: se no .ui existe um QPushButton com objectName="loadButton"

        self.load_button = self.findChild(QPushButton, "loadButton")
        if self.load_button:
            # Configuração adicional se necessário
            pass

    def _connect_signals(self):
        """Conecta signals dos widgets"""
        if hasattr(self, 'load_button') and self.load_button:
            self.load_button.clicked.connect(self._on_load_clicked)

    def _on_load_clicked(self):
        """Handler para clique no botão"""
        print("Botão clicado!")
'''

    sample_path = SRC_DIR / "desktop" / "widgets" / "_migrated_widget_example.py"
    sample_path.write_text(sample, encoding="utf-8")
    print(f"\n✅ Exemplo salvo em: {sample_path}")
    return sample_path


def main():
    """Executa análise e gera instruções"""

    print("=" * 70)
    print("🔄 MIGRAÇÃO FASE 2 - CONEXÃO CLASSES PYTHON ↔ ARQUIVOS .UI")
    print("=" * 70)

    # 1. Verificar arquivos .ui
    check_ui_files_exist()

    # 2. Verificar classes Python
    results = check_python_classes()

    # 3. Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)

    total = len(CLASS_TO_UI_MAP)
    connected = len(results["connected"])
    not_connected = len(results["not_connected"])
    not_found = len(results["not_found"])

    print(f"""
   Total de classes para migrar: {total}
   ✅ Já conectadas: {connected}
   ⚠️ Aguardando conexão: {not_connected}
   ❓ Não encontradas: {not_found}

   Progresso: {connected}/{total} ({100*connected/total:.1f}%)
""")

    # 4. Gerar instruções
    if not_connected > 0:
        generate_migration_instructions()

    # 5. Criar exemplo
    create_sample_migrated_class()

    print("\n" + "=" * 70)
    print("📝 PRÓXIMOS PASSOS")
    print("=" * 70)
    print("""
Para completar a Fase 2, cada classe precisa ser modificada manualmente:

1. Abrir o arquivo .py da classe
2. Adicionar import do UiLoaderMixin
3. Adicionar UiLoaderMixin à herança
4. Adicionar UI_FILE com o caminho do .ui
5. Chamar load_ui() no __init__
6. Adaptar _setup_ui() para usar widgets do .ui

Após migrar todas as classes, execute pytest para validar.
""")


if __name__ == "__main__":
    main()
