"""
Sistema de Internacionalização (i18n) - Platform Base v2.0

Sistema para localização da aplicação em português brasileiro.
"""

import json


# Dicionário de traduções pt-BR
TRANSLATIONS_PT_BR: dict[str, str] = {
    # Aplicação principal
    "Platform Base": "Platform Base",
    "Time Series Analysis": "Análise de Séries Temporais",
    "Starting Platform Base v2.0...": "Iniciando Platform Base v2.0...",

    # Menu principal
    "&File": "&Arquivo",
    "File": "Arquivo",
    "&Edit": "&Editar",
    "Edit": "Editar",
    "&View": "&Visualizar",
    "View": "Visualizar",
    "&Analysis": "&Análise",
    "Analysis": "Análise",
    "&Tools": "&Ferramentas",
    "Tools": "Ferramentas",
    "&Help": "A&juda",
    "Help": "Ajuda",

    # Submenu Arquivo
    "&New Session": "&Nova Sessão",
    "&Open Session...": "&Abrir Sessão...",
    "&Save Session...": "&Salvar Sessão...",
    "&Load Data...": "&Carregar Dados...",
    "E&xit": "S&air",
    "New": "Novo",
    "Open": "Abrir",
    "Open File": "Abrir Arquivo",
    "Recent Files": "Arquivos Recentes",
    "Save": "Salvar",
    "Save As": "Salvar Como",
    "Export": "Exportar",
    "Import": "Importar",
    "Close": "Fechar",
    "Exit": "Sair",

    # Submenu Editar
    "Undo": "Desfazer",
    "Redo": "Refazer",
    "Cut": "Recortar",
    "Copy": "Copiar",
    "Paste": "Colar",
    "Select All": "Selecionar Tudo",
    "Clear Selection": "Limpar Seleção",
    "Preferences": "Preferências",

    # Submenu Visualizar
    "Data Panel": "Painel de Dados",
    "Visualization Panel": "Painel de Visualização",
    "Configuration Panel": "Painel de Configuração",
    "Results Panel": "Painel de Resultados",
    "Toolbar": "Barra de Ferramentas",
    "Status Bar": "Barra de Status",
    "Full Screen": "Tela Cheia",

    # Submenu Análise
    "Mathematical Analysis": "Análise Matemática",
    "Statistical Analysis": "Análise Estatística",
    "Signal Processing": "Processamento de Sinais",
    "Data Processing": "Processamento de Dados",
    "Filtering": "Filtragem",
    "Interpolation": "Interpolação",
    "Derivatives": "Derivadas",
    "Integrals": "Integrais",

    # Submenu Ajuda
    "About": "Sobre",
    "User Guide": "Manual do Usuário",
    "Technical Documentation": "Documentação Técnica",
    "Keyboard Shortcuts": "Atalhos do Teclado",
    "Report Bug": "Reportar Bug",

    # Temas
    "Light Theme": "Tema Claro",
    "Dark Theme": "Tema Escuro",
    "Auto Theme": "Tema Automático",

    # Configurações
    "Platform Base Settings": "Configurações Platform Base",
    "&Settings...": "&Configurações...",
    "&About...": "&Sobre...",
    "General": "Geral",
    "Performance": "Performance",
    "Logging": "Logs",
    "Restore Defaults": "Restaurar Padrões",
    "Apply": "Aplicar",
    "Are you sure you want to restore all settings to their default values?": "Tem certeza de que deseja restaurar todas as configurações para os valores padrão?",
    "Settings": "Configurações",
    "Default settings restored.": "Configurações padrão restauradas.",
    "Settings Error": "Erro de Configurações",
    "Failed to apply settings": "Falha ao aplicar configurações",

    # Configurações Gerais
    "Appearance": "Aparência",
    "Auto": "Automático",
    "Light": "Claro",
    "Dark": "Escuro",
    "Theme:": "Tema:",
    "Font Size:": "Tamanho da Fonte:",
    "Enable high DPI scaling": "Habilitar escala high DPI",
    "Display:": "Tela:",
    "Behavior": "Comportamento",
    " minutes": " minutos",
    "Auto-save interval:": "Intervalo de salvamento automático:",
    "Confirm before exiting": "Confirmar antes de sair",
    "Exit:": "Saída:",
    "Remember window position and size": "Lembrar posição e tamanho da janela",
    "Window:": "Janela:",

    # Configurações de Performance
    "Memory Management": "Gerenciamento de Memória",
    " MB": " MB",
    "Memory Cache Size:": "Tamanho do Cache de Memória:",
    "Max Datasets in Memory:": "Máx. Conjuntos de Dados na Memória:",
    "Disk Cache": "Cache em Disco",
    "Enable disk cache": "Habilitar cache em disco",
    "Cache:": "Cache:",
    "Cache Directory:": "Diretório do Cache:",
    "Cache Size Limit:": "Limite do Tamanho do Cache:",
    "Processing": "Processamento",
    "Worker Threads:": "Threads de Trabalho:",
    "Use Numba acceleration (requires restart)": "Usar aceleração Numba (requer reinicialização)",
    "Acceleration:": "Aceleração:",
    "Select Cache Directory": "Selecionar Diretório do Cache",

    # Configurações de Logging
    "Logging Level": "Nível de Log",
    "Log Level:": "Nível de Log:",
    "Log Destinations": "Destinos de Log",
    "Log to console": "Log no console",
    "Console:": "Console:",
    "Log to file": "Log em arquivo",
    "File:": "Arquivo:",
    "Log File:": "Arquivo de Log:",
    "Log Format": "Formato de Log",
    "Select Log File": "Selecionar Arquivo de Log",
    "Log Files (*.log);;Text Files (*.txt);;All Files (*)": "Arquivos de Log (*.log);;Arquivos de Texto (*.txt);;Todos os Arquivos (*)",

    # Toolbar
    "Main": "Principal",
    "Load Data": "Carregar Dados",

    # Painéis
    "Datasets & Series": "Conjuntos de Dados e Séries",
    "Data Information": "Informações dos Dados",
    "Summary": "Resumo",
    "Metadata": "Metadados",
    "Quality": "Qualidade",

    # Botões gerais
    "OK": "OK",
    "Cancel": "Cancelar",
    "Yes": "Sim",
    "No": "Não",
    "Browse": "Procurar",
    "Load": "Carregar",
    "Delete": "Excluir",
    "Remove": "Remover",
    "Add": "Adicionar",
    "Refresh": "Atualizar",

    # Dialog de Upload
    "Load Data Files": "Carregar Arquivos de Dados",
    "File Upload": "Carregamento de Arquivo",
    "Select File": "Selecionar Arquivo",
    "File Selection": "Seleção de Arquivo",
    "Select file to load...": "Selecione arquivo para carregar...",
    "Browse...": "Procurar...",
    "Format: Not detected": "Formato: Não detectado",
    "Configuration": "Configuração",
    "Preview": "Visualização",
    "Progress": "Progresso",
    "Generate Preview": "Gerar Visualização",
    "Select a file to begin": "Selecione um arquivo para começar",
    "File selected. Configure options or generate preview.": "Arquivo selecionado. Configure as opções ou gere uma visualização.",
    "Select Data File": "Selecionar Arquivo de Dados",
    "Data Preview:": "Visualização dos Dados:",
    "Load Error": "Erro de Carregamento",
    "Failed to load file": "Falha ao carregar arquivo",

    # Configurações de arquivo
    "General Settings": "Configurações Gerais",
    "File Format": "Formato do Arquivo",
    "Format": "Formato",
    "Delimiter": "Delimitador",
    "Delimiter:": "Delimitador:",
    "Encoding": "Codificação",
    "Encoding:": "Codificação:",
    "Header Row": "Linha de Cabeçalho",
    "Skip Rows": "Pular Linhas",
    "Skip Rows:": "Pular Linhas:",
    "Date Format": "Formato de Data",
    "Time Column": "Coluna de Tempo",
    "Schema Detection": "Detecção de Schema",
    "Timestamp Column:": "Coluna de Timestamp:",
    "Auto-detect": "Detectar Automaticamente",
    "Excel Settings": "Configurações do Excel",
    "Sheet:": "Planilha:",
    "HDF5 Settings": "Configurações HDF5",
    "Key:": "Chave:",
    "Advanced Options": "Opções Avançadas",
    "Use chunked loading": "Usar carregamento em blocos",
    "Performance:": "Performance:",
    "Chunk Size:": "Tamanho do Bloco:",

    # Visualização de dados
    "Plot": "Gráfico",
    "2D Plot": "Gráfico 2D",
    "3D Plot": "Gráfico 3D",
    "Create Plot": "Criar Gráfico",
    "Plot Settings": "Configurações do Gráfico",
    "Line Width": "Largura da Linha",
    "Show Grid": "Mostrar Grade",
    "Show Legend": "Mostrar Legenda",
    "Active Series": "Séries Ativas",

    # Ferramentas de seleção
    "Selection Tools": "Ferramentas de Seleção",
    "Type": "Tipo",
    "Mode": "Modo",
    "Temporal": "Temporal",
    "Graphical": "Gráfica",
    "Conditional": "Condicional",
    "Replace": "Substituir",
    "Subtract": "Subtrair",
    "Intersect": "Interseção",
    "Clear": "Limpar",

    # Análise matemática
    "Calculate Derivative": "Calcular Derivada",
    "Calculate Integral": "Calcular Integral",
    "Show Statistics": "Mostrar Estatísticas",
    "FFT Analysis": "Análise FFT",
    "Correlation Analysis": "Análise de Correlação",
    "Smooth Data": "Suavizar Dados",
    "Interpolate Missing Data": "Interpolar Dados Ausentes",
    "Resample Data": "Reamostrar Dados",
    "Filters": "Filtros",
    "Low-pass Filter": "Filtro Passa-Baixa",
    "High-pass Filter": "Filtro Passa-Alta",
    "Band-pass Filter": "Filtro Passa-Banda",
    "Detect Outliers": "Detectar Outliers",

    # Controles de visualização
    "Zoom to Selection": "Zoom na Seleção",
    "Reset Zoom": "Resetar Zoom",
    "Toggle Grid": "Alternar Grade",
    "Toggle Legend": "Alternar Legenda",
    "Add Annotation": "Adicionar Anotação",
    "Export Plot": "Exportar Gráfico",
    "Export Data": "Exportar Dados",
    "Copy to Clipboard": "Copiar para Área de Transferência",
    "Add Y Axis": "Adicionar Eixo Y",
    "Move to Y2": "Mover para Y2",
    "Select": "Selecionar",

    # Gerenciamento de séries
    "Duplicate Series": "Duplicar Série",
    "Hide Series": "Ocultar Série",
    "Remove Series": "Remover Série",
    "Series Properties": "Propriedades da Série",

    # Estatísticas
    "Statistics": "Estatísticas",
    "Count": "Contagem",
    "Mean": "Média",
    "Std Dev": "Desvio Padrão",
    "Min": "Mínimo",
    "Max": "Máximo",
    "Median": "Mediana",
    "Skewness": "Assimetria",
    "Kurtosis": "Curtose",

    # Seleção estatísticas
    "Selection Statistics": "Estatísticas da Seleção",
    "Total Points": "Total de Pontos",
    "Selected": "Selecionados",
    "Percentage": "Porcentagem",
    "Value Statistics": "Estatísticas de Valores",
    "Minimum": "Mínimo",
    "Maximum": "Máximo",
    "Time Range": "Intervalo de Tempo",
    "Ranges": "Intervalos",
    "Total Duration": "Duração Total",

    # Dialog de seleção condicional
    "Conditional Selection": "Seleção Condicional",
    "Selection Condition": "Condição de Seleção",
    "Quick Conditions": "Condições Rápidas",
    "Value threshold": "Limite de valor",
    "Apply Threshold": "Aplicar Limite",
    "Top/bottom percentile": "Percentil superior/inferior",
    "Top": "Superior",
    "Bottom": "Inferior",
    "Apply Percentile": "Aplicar Percentil",
    "Selection Mode": "Modo de Seleção",
    "Apply Selection": "Aplicar Seleção",

    # Formatos de exportação
    "PNG": "PNG",
    "SVG": "SVG",
    "PDF": "PDF",
    "JPEG": "JPEG",
    "CSV": "CSV",
    "Excel": "Excel",

    # Métodos de interpolação
    "Linear": "Linear",
    "Cubic Spline": "Spline Cúbica",
    "Smoothing Spline": "Spline Suavizada",
    "Moving Least Squares": "Mínimos Quadrados Móveis",
    "Gaussian Process": "Processo Gaussiano",
    "Spectral": "Espectral",

    # Métodos de derivada
    "Finite Difference": "Diferença Finita",
    "Savitzky-Golay": "Savitzky-Golay",
    "Spline Derivative": "Derivada por Spline",

    # Métodos de integral
    "Trapezoid": "Trapézio",
    "Simpson": "Simpson",
    "Cumulative": "Cumulativa",

    # Métodos de reamostragem
    "LTTB": "LTTB",
    "MinMax": "MínMáx",
    "Adaptive": "Adaptativa",
    "Uniform": "Uniforme",
    "Peak Aware": "Consciente de Picos",

    # Parâmetros de análise
    "Order": "Ordem",
    "Method": "Método",
    "Window Size": "Tamanho da Janela",
    "Polynomial Order": "Ordem do Polinômio",
    "Target Points": "Pontos Alvo",
    "Apply smoothing": "Aplicar suavização",

    # Mensagens de erro
    "Error": "Erro",
    "Warning": "Aviso",
    "Information": "Informação",
    "Failed to generate preview": "Falha ao gerar visualização",
    "Preview Error": "Erro de Visualização",
    "File not found": "Arquivo não encontrado",
    "Invalid file format": "Formato de arquivo inválido",
    "No data available": "Nenhum dado disponível",

    # Status e progresso
    "Ready": "Pronto",
    "Loading": "Carregando",
    "Processing": "Processando",
    "Completed": "Concluído",
    "Cancelled": "Cancelado",
    "Failed": "Falhou",

    # Welcome screen
    "Welcome": "Bem-vindo",
    "Platform Base Visualization": "Visualização Platform Base",
    "Welcome to the visualization panel!": "Bem-vindo ao painel de visualização!",
    "Getting Started": "Primeiros Passos",
    "Load data using the Data panel": "Carregue dados usando o painel de Dados",
    "Select series to plot": "Selecione séries para plotar",
    "Double-click series to create plots": "Clique duas vezes nas séries para criar gráficos",
    "Use toolbar to create 2D/3D plots": "Use a barra de ferramentas para criar gráficos 2D/3D",
    "Interaction": "Interação",
    "Ctrl+Click to start time selection": "Ctrl+Clique para iniciar seleção de tempo",
    "Mouse wheel to zoom": "Roda do mouse para zoom",
    "Drag to pan": "Arrastar para panorâmica",
    "Right-click for context menu": "Clique direito para menu contextual",

    # Tipos de dados
    "Dataset": "Conjunto de Dados",
    "Series": "Série",
    "Original": "Original",
    "Derived": "Derivada",
    "Loaded": "Carregado",

    # Unidades de tempo
    "seconds": "segundos",
    "minutes": "minutos",
    "hours": "horas",
    "days": "dias",
    "Time (s)": "Tempo (s)",
    "Value": "Valor",

    # Dialog Sobre
    "About Platform Base": "Sobre Platform Base",
    "Logo": "Logo",
    "Version 2.0.0": "Versão 2.0.0",
    "Time Series Analysis Tool": "Ferramenta de Análise de Séries Temporais",
    "Credits": "Créditos",
    "System": "Sistema",
    "License": "Licença",
    "Version": "Versão",
    "Build": "Build",
    "Copyright": "Copyright",

    # Menu de contexto do gráfico
    "📊 Mathematical Analysis": "📊 Análise Matemática",
    "📈 Calculate Derivative...": "📈 Calcular Derivada...",
    "📉 Calculate Integral...": "📉 Calcular Integral...",
    "📊 Show Statistics": "📊 Mostrar Estatísticas",
    "🌊 FFT Analysis": "🌊 Análise FFT",
    "🔗 Correlation Analysis": "🔗 Análise de Correlação",
    "🔧 Data Processing": "🔧 Processamento de Dados",
    "🌊 Smooth Data...": "🌊 Suavizar Dados...",
    "🎯 Interpolate Missing Data...": "🎯 Interpolar Dados Ausentes...",
    "📏 Resample Data...": "📏 Reamostrar Dados...",
    "🔍 Filters": "🔍 Filtros",
    "🎯 Detect Outliers": "🎯 Detectar Outliers",
    "👁️ Visualization": "👁️ Visualização",
    "🔍 Zoom to Selection": "🔍 Zoom na Seleção",
    "🔄 Reset Zoom": "🔄 Resetar Zoom",
    "⊞ Toggle Grid": "⊞ Alternar Grade",
    "📝 Toggle Legend": "📝 Alternar Legenda",
    "📝 Add Annotation...": "📝 Adicionar Anotação...",
    "🗑️ Clear Selection": "🗑️ Limpar Seleção",
    "☑️ Select All": "☑️ Selecionar Tudo",
    "🔄 Invert Selection": "🔄 Inverter Seleção",
    "💾 Export": "💾 Exportar",
    "🖼️ Export Plot": "🖼️ Exportar Gráfico",
    "📊 Export Data...": "📊 Exportar Dados...",
    "📋 Copy to Clipboard": "📋 Copiar para Área de Transferência",
    "📄 Duplicate Series": "📄 Duplicar Série",
    "👁️ Hide Series": "👁️ Ocultar Série",
    "🗑️ Remove Series": "🗑️ Remover Série",
    "⚙️ Series Properties...": "⚙️ Propriedades da Série...",

    # Diálogos de análise matemática
    "Mathematical Analysis -": "Análise Matemática -",
    "Derivative Parameters": "Parâmetros da Derivada",
    "Integration Parameters": "Parâmetros de Integração",
    "Smoothing Parameters": "Parâmetros de Suavização",
    "Interpolation Parameters": "Parâmetros de Interpolação",
    "Resampling Parameters": "Parâmetros de Reamostragem",
    "Order:": "Ordem:",
    "Method:": "Método:",
    "Window size:": "Tamanho da janela:",
    "Window Size:": "Tamanho da Janela:",
    "Polynomial Order:": "Ordem Polinomial:",
    "Target Points:": "Pontos Alvo:",

    # Métodos específicos
    "finite_diff": "Diferença Finita",
    "savitzky_golay": "Savitzky-Golay",
    "spline_derivative": "Derivada por Spline",
    "trapezoid": "Trapézio",
    "simpson": "Simpson",
    "cumulative": "Cumulativo",
    "moving_average": "Média Móvel",
    "gaussian": "Gaussiano",
    "lowpass_filter": "Filtro Passa-Baixa",
    "median_filter": "Filtro de Mediana",
    "spline_cubic": "Spline Cúbica",
    "smoothing_spline": "Spline Suavizada",
    "mls": "MLS",
    "gpr": "GPR",
    "lomb_scargle_spectral": "Espectral Lomb-Scargle",
    "lttb": "LTTB",
    "minmax": "MínMáx",
    "adaptive": "Adaptativo",
    "uniform": "Uniforme",

    # Estatísticas e propriedades
    "Statistics -": "Estatísticas -",
    "Q25": "Q25",
    "Q75": "Q75",
    "Failed to calculate statistics": "Falha ao calcular estatísticas",

    # Mensagens de funcionalidades futuras
    "FFT analysis feature coming soon!": "Funcionalidade de análise FFT em breve!",
    "Correlation analysis feature coming soon!": "Funcionalidade de análise de correlação em breve!",
    " filter feature coming soon!": " filtro em breve!",
    "Outlier detection feature coming soon!": "Detecção de outliers em breve!",
    "Copy to clipboard feature coming soon!": "Copiar para área de transferência em breve!",
    "Series properties dialog coming soon!": "Diálogo de propriedades da série em breve!",
    "Remove series": "Remover série",
    "Annotation text:": "Texto da anotação:",

    # Atalhos de teclado comuns
    "Ctrl+O": "Ctrl+O",
    "Ctrl+S": "Ctrl+S",
    "Ctrl+Z": "Ctrl+Z",
    "Ctrl+Y": "Ctrl+Y",
    "Ctrl+C": "Ctrl+C",
    "Ctrl+V": "Ctrl+V",
    "Ctrl+A": "Ctrl+A",
    "Escape": "Escape",
    "F1": "F1",
    "F11": "F11",
}

# Classe para gerenciar traduções
class I18n:
    """Sistema de internacionalização"""

    def __init__(self, language: str = "pt-BR"):
        self.language = language
        self._translations = TRANSLATIONS_PT_BR if language == "pt-BR" else {}

    def tr(self, text: str) -> str:
        """Traduz um texto para o idioma atual"""
        return self._translations.get(text, text)

    def set_language(self, language: str) -> None:
        """Define o idioma da aplicação"""
        self.language = language
        if language == "pt-BR":
            self._translations = TRANSLATIONS_PT_BR
        else:
            self._translations = {}

    def get_language(self) -> str:
        """Retorna o idioma atual"""
        return self.language

    def add_translation(self, original: str, translation: str) -> None:
        """Adiciona uma tradução personalizada"""
        self._translations[original] = translation

    def save_translations(self, filepath: str) -> None:
        """Salva as traduções em um arquivo JSON"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self._translations, f, ensure_ascii=False, indent=2)

    def load_translations(self, filepath: str) -> None:
        """Carrega traduções de um arquivo JSON"""
        try:
            with open(filepath, encoding="utf-8") as f:
                self._translations.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            pass

# Instância global do sistema de internacionalização
_i18n = I18n("pt-BR")

def tr(text: str) -> str:
    """Função de conveniência para tradução"""
    return _i18n.tr(text)

def set_language(language: str) -> None:
    """Define o idioma da aplicação"""
    _i18n.set_language(language)

def get_language() -> str:
    """Retorna o idioma atual"""
    return _i18n.get_language()

def get_i18n() -> I18n:
    """Retorna a instância do sistema de internacionalização"""
    return _i18n
