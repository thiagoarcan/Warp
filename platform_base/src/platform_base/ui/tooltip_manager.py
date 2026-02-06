"""
Tooltip Manager - Sistema centralizado de tooltips

Adiciona tooltips descritivos a todos os componentes da UI
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QAction, QDockWidget


class TooltipManager:
    """
    Gerenciador centralizado de tooltips.
    
    Adiciona tooltips informativos a todos os componentes da interface,
    explicando a função de cada elemento.
    """
    
    # Tooltips para ações do menu
    MENU_TOOLTIPS = {
        # Arquivo
        "new_session": "Cria uma nova sessão de análise (Ctrl+N)",
        "open_session": "Abre uma sessão salva anteriormente (Ctrl+O)",
        "save_session": "Salva a sessão atual com todos os dados e configurações (Ctrl+S)",
        "load_data": "Carrega dados de arquivo (CSV, Excel, HDF5, Parquet) (Ctrl+L)",
        "export_data": "Exporta dados selecionados para arquivo (Ctrl+E)",
        "exit": "Fecha a aplicação (Ctrl+Q)",
        
        # Editar
        "undo": "Desfaz a última operação (Ctrl+Z)",
        "redo": "Refaz a última operação desfeita (Ctrl+Y)",
        "find_series": "Busca série pelo nome (Ctrl+F)",
        "delete": "Remove série ou seleção atual (Delete)",
        
        # Visualizar
        "refresh": "Atualiza visualização com dados mais recentes (F5)",
        "fullscreen": "Alterna modo tela cheia (F11)",
        "redock": "Re-doca todos os painéis destacados (Ctrl+Shift+D)",
        
        # Ferramentas
        "settings": "Abre configurações da aplicação",
        "xlsx_converter": "Converte arquivos Excel (.xlsx) para CSV",
        
        # Ajuda
        "help_contextual": "Mostra ajuda contextual (F1)",
        "keyboard_shortcuts": "Lista todos os atalhos de teclado",
        "about": "Informações sobre a aplicação",
    }
    
    # Tooltips para painéis
    PANEL_TOOLTIPS = {
        "data_panel": "Painel de Dados - Gerencia datasets, séries temporais e seleção de dados",
        "viz_panel": "Painel de Visualização - Gráficos 2D/3D interativos com zoom e seleção",
        "config_panel": "Painel de Configurações - Temas, performance e preferências",
        "operations_panel": "Painel de Operações - Interpolação, cálculos, filtros e transformações",
        "streaming_panel": "Painel de Streaming - Reprodução temporal de dados com controles de playback",
        "results_panel": "Painel de Resultados - Estatísticas e métricas das operações",
        "resource_monitor_panel": "Monitor de Recursos - Uso de CPU, RAM e Disco em tempo real",
        "activity_log_panel": "Log de Atividades - Registro detalhado de todas as operações executadas",
        "data_tables_panel": "Tabelas de Dados - Visualização tabular de dados brutos, interpolados, sincronizados",
    }
    
    # Tooltips para botões comuns
    BUTTON_TOOLTIPS = {
        "load": "Carrega dados de arquivo",
        "save": "Salva dados ou sessão",
        "export": "Exporta dados para arquivo",
        "import": "Importa dados de arquivo",
        "clear": "Limpa dados ou seleção atual",
        "apply": "Aplica operação ou configuração",
        "cancel": "Cancela operação em andamento",
        "close": "Fecha janela ou diálogo",
        "ok": "Confirma e fecha",
        "refresh": "Atualiza dados ou visualização",
        "reset": "Restaura valores padrão",
        "browse": "Abre diálogo de seleção de arquivo",
        "add": "Adiciona novo item",
        "remove": "Remove item selecionado",
        "edit": "Edita item selecionado",
        "copy": "Copia para área de transferência",
        "paste": "Cola da área de transferência",
        "undo": "Desfaz última operação",
        "redo": "Refaz operação desfeita",
        "play": "Inicia reprodução",
        "pause": "Pausa reprodução",
        "stop": "Para reprodução",
        "previous": "Item anterior",
        "next": "Próximo item",
        "zoom_in": "Aumenta zoom",
        "zoom_out": "Diminui zoom",
        "zoom_reset": "Restaura zoom original",
        "fit": "Ajusta visualização ao conteúdo",
    }
    
    @staticmethod
    def add_menu_tooltips(main_window):
        """
        Adiciona tooltips a todas as ações de menu.
        
        Args:
            main_window: Instância de ModernMainWindow
        """
        tooltip_map = {
            # Arquivo
            "actionNewSession": "new_session",
            "actionOpenSession": "open_session",
            "actionSaveSession": "save_session",
            "actionLoadData": "load_data",
            "actionExportData": "export_data",
            "actionExit": "exit",
            
            # Editar
            "actionUndo": "undo",
            "actionRedo": "redo",
            "actionFindSeries": "find_series",
            
            # Visualizar
            "actionRefreshData": "refresh",
            "actionFullscreen": "fullscreen",
            
            # Ferramentas
            "actionSettings": "settings",
            
            # Ajuda
            "actionContextualHelp": "help_contextual",
            "actionKeyboardShortcuts": "keyboard_shortcuts",
            "actionAbout": "about",
        }
        
        for attr_name, tooltip_key in tooltip_map.items():
            if hasattr(main_window, attr_name):
                action = getattr(main_window, attr_name)
                if isinstance(action, QAction):
                    tooltip = TooltipManager.MENU_TOOLTIPS.get(tooltip_key)
                    if tooltip:
                        action.setToolTip(tooltip)
                        action.setStatusTip(tooltip)
    
    @staticmethod
    def add_panel_tooltips(main_window):
        """
        Adiciona tooltips a todos os painéis (docks).
        
        Args:
            main_window: Instância de ModernMainWindow
        """
        panel_map = {
            "data_dock": "data_panel",
            "viz_panel": "viz_panel",
            "config_dock": "config_panel",
            "operations_dock": "operations_panel",
            "streaming_dock": "streaming_panel",
            "results_dock": "results_panel",
            "resource_monitor_dock": "resource_monitor_panel",
            "activity_log_dock": "activity_log_panel",
            "data_tables_dock": "data_tables_panel",
        }
        
        for attr_name, tooltip_key in panel_map.items():
            if hasattr(main_window, attr_name):
                dock = getattr(main_window, attr_name)
                if isinstance(dock, (QDockWidget, QWidget)):
                    tooltip = TooltipManager.PANEL_TOOLTIPS.get(tooltip_key)
                    if tooltip:
                        dock.setToolTip(tooltip)
    
    @staticmethod
    def add_button_tooltip(button: QPushButton, button_type: str):
        """
        Adiciona tooltip a um botão específico.
        
        Args:
            button: Instância de QPushButton
            button_type: Tipo do botão (chave em BUTTON_TOOLTIPS)
        """
        tooltip = TooltipManager.BUTTON_TOOLTIPS.get(button_type)
        if tooltip:
            button.setToolTip(tooltip)
    
    @staticmethod
    def add_custom_tooltip(widget: QWidget, tooltip: str):
        """
        Adiciona tooltip customizado a um widget.
        
        Args:
            widget: Widget qualquer
            tooltip: Texto do tooltip
        """
        widget.setToolTip(tooltip)
    
    @staticmethod
    def add_all_tooltips(main_window):
        """
        Adiciona todos os tooltips à janela principal.
        
        Args:
            main_window: Instância de ModernMainWindow
        """
        TooltipManager.add_menu_tooltips(main_window)
        TooltipManager.add_panel_tooltips(main_window)
