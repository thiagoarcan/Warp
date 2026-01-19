from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any, Union
from enum import Enum
import json

import dash
from dash import html, dcc, Input, Output, State, callback_context
import plotly.graph_objects as go

from platform_base.core.models import ViewData, Dataset
from platform_base.ui.selection import DataSelector, SelectionMode
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class MenuActionType(Enum):
    """Tipos de ações do context menu conforme PRD seção 10.5"""
    SELECTION = "selection"         # Ações de seleção
    ANALYSIS = "analysis"          # Análises e cálculos
    VISUALIZATION = "visualization" # Mudanças de visualização
    EXPORT = "export"              # Exportação de dados
    ANNOTATION = "annotation"      # Anotações e marcações
    TRANSFORMATION = "transformation" # Transformações de dados


@dataclass
class MenuActionContext:
    """Contexto disponível para ações do menu"""
    click_data: Optional[Dict] = None
    selection_data: Optional[Dict] = None
    figure_data: Optional[go.Figure] = None
    view_data: Optional[ViewData] = None
    dataset: Optional[Dataset] = None
    selected_series: List[str] = field(default_factory=list)
    coordinates: Optional[tuple] = None  # (x, y) do clique
    
    @property
    def has_selection(self) -> bool:
        """Verifica se há dados selecionados"""
        return (self.selection_data is not None and 
                len(self.selection_data.get('points', [])) > 0)
    
    @property
    def selected_points(self) -> List[int]:
        """Retorna índices dos pontos selecionados"""
        if not self.has_selection:
            return []
        return [p.get('pointIndex') for p in self.selection_data.get('points', [])
                if p.get('pointIndex') is not None]


@dataclass
class MenuAction:
    """Ação do context menu"""
    id: str
    name: str
    handler: Callable[[MenuActionContext], Any]
    action_type: MenuActionType
    description: str = ""
    icon: str = ""
    enabled_predicate: Optional[Callable[[MenuActionContext], bool]] = None
    requires_selection: bool = False
    
    def is_enabled(self, context: MenuActionContext) -> bool:
        """Verifica se ação está habilitada no contexto atual"""
        if self.requires_selection and not context.has_selection:
            return False
        
        if self.enabled_predicate:
            return self.enabled_predicate(context)
        
        return True


class ContextMenuManager:
    """
    Gerenciador de context menus para gráficos Plotly conforme PRD seção 10.5
    
    Integra-se com callbacks do Dash para fornecer menus contextuais
    dinâmicos baseados no estado atual da visualização.
    """
    
    def __init__(self):
        self.actions: Dict[str, MenuAction] = {}
        self.data_selector = DataSelector()
        self._register_default_actions()
    
    def register_action(self, action: MenuAction):
        """Registra nova ação no menu"""
        self.actions[action.id] = action
        logger.debug("context_menu_action_registered", 
                    action_id=action.id, action_type=action.action_type.value)
    
    def unregister_action(self, action_id: str):
        """Remove ação do menu"""
        if action_id in self.actions:
            del self.actions[action_id]
            logger.debug("context_menu_action_unregistered", action_id=action_id)
    
    def get_menu_items(self, context: MenuActionContext) -> List[Dict[str, Any]]:
        """
        Gera itens do menu baseado no contexto atual
        
        Args:
            context: Contexto da interação
            
        Returns:
            Lista de itens do menu formatados para o frontend
        """
        enabled_actions = []
        
        for action in self.actions.values():
            if action.is_enabled(context):
                enabled_actions.append({
                    "id": action.id,
                    "name": action.name,
                    "description": action.description,
                    "icon": action.icon,
                    "type": action.action_type.value
                })
        
        # Agrupa por tipo para melhor organização
        grouped_items = {}
        for item in enabled_actions:
            action_type = item["type"]
            if action_type not in grouped_items:
                grouped_items[action_type] = []
            grouped_items[action_type].append(item)
        
        return grouped_items
    
    def execute_action(self, action_id: str, context: MenuActionContext) -> Any:
        """
        Executa ação do menu
        
        Args:
            action_id: ID da ação a executar
            context: Contexto da execução
            
        Returns:
            Resultado da execução da ação
        """
        if action_id not in self.actions:
            logger.error("context_menu_action_not_found", action_id=action_id)
            raise ValueError(f"Ação '{action_id}' não encontrada")
        
        action = self.actions[action_id]
        
        if not action.is_enabled(context):
            logger.warning("context_menu_action_disabled", action_id=action_id)
            raise ValueError(f"Ação '{action_id}' não está habilitada no contexto atual")
        
        try:
            logger.info("context_menu_action_executing", action_id=action_id)
            result = action.handler(context)
            logger.info("context_menu_action_completed", action_id=action_id)
            return result
            
        except Exception as e:
            logger.error("context_menu_action_failed", 
                        action_id=action_id, error=str(e))
            raise
    
    def create_dash_component(self, graph_id: str) -> html.Div:
        """
        Cria componente Dash para o context menu
        
        Args:
            graph_id: ID do componente de gráfico associado
            
        Returns:
            Componente Dash com o menu contextual
        """
        menu_id = f"{graph_id}-context-menu"
        overlay_id = f"{graph_id}-menu-overlay"
        
        return html.Div([
            # Overlay invisível para capturar cliques
            html.Div(
                id=overlay_id,
                style={
                    "position": "absolute",
                    "top": 0,
                    "left": 0,
                    "width": "100%",
                    "height": "100%",
                    "z-index": 1000,
                    "display": "none",
                    "background": "rgba(0,0,0,0.1)"
                }
            ),
            
            # Menu contextual
            html.Div(
                id=menu_id,
                children=[],
                style={
                    "position": "absolute",
                    "background": "white",
                    "border": "1px solid #ccc",
                    "border-radius": "4px",
                    "box-shadow": "0 2px 10px rgba(0,0,0,0.2)",
                    "min-width": "150px",
                    "z-index": 1001,
                    "display": "none",
                    "padding": "5px"
                }
            ),
            
            # Store para dados do contexto
            dcc.Store(id=f"{graph_id}-context-data"),
            dcc.Store(id=f"{graph_id}-menu-state")
        ])
    
    def _register_default_actions(self):
        """Registra ações padrão do context menu"""
        
        # Ações de seleção
        self.register_action(MenuAction(
            id="select_all",
            name="Select All Points",
            handler=self._action_select_all,
            action_type=MenuActionType.SELECTION,
            description="Select all visible points",
            icon="select-all"
        ))
        
        self.register_action(MenuAction(
            id="select_time_window",
            name="Select Time Window",
            handler=self._action_select_time_window,
            action_type=MenuActionType.SELECTION,
            description="Select points in time window",
            icon="clock",
            enabled_predicate=lambda ctx: ctx.coordinates is not None
        ))
        
        self.register_action(MenuAction(
            id="clear_selection",
            name="Clear Selection",
            handler=self._action_clear_selection,
            action_type=MenuActionType.SELECTION,
            description="Clear current selection",
            icon="clear",
            requires_selection=True
        ))
        
        # Ações de análise
        self.register_action(MenuAction(
            id="calculate_statistics",
            name="Calculate Statistics",
            handler=self._action_calculate_stats,
            action_type=MenuActionType.ANALYSIS,
            description="Show basic statistics",
            icon="calculator",
            requires_selection=True
        ))
        
        self.register_action(MenuAction(
            id="fit_trend",
            name="Fit Linear Trend",
            handler=self._action_fit_trend,
            action_type=MenuActionType.ANALYSIS,
            description="Fit linear trend to selection",
            icon="trending-up",
            requires_selection=True
        ))
        
        # Ações de visualização
        self.register_action(MenuAction(
            id="zoom_to_selection",
            name="Zoom to Selection",
            handler=self._action_zoom_to_selection,
            action_type=MenuActionType.VISUALIZATION,
            description="Zoom plot to selected data",
            icon="zoom-in",
            requires_selection=True
        ))
        
        self.register_action(MenuAction(
            id="add_annotation",
            name="Add Annotation",
            handler=self._action_add_annotation,
            action_type=MenuActionType.ANNOTATION,
            description="Add text annotation at point",
            icon="message",
            enabled_predicate=lambda ctx: ctx.coordinates is not None
        ))
        
        # Ações de exportação
        self.register_action(MenuAction(
            id="export_selection",
            name="Export Selection",
            handler=self._action_export_selection,
            action_type=MenuActionType.EXPORT,
            description="Export selected data",
            icon="download",
            requires_selection=True
        ))
    
    # Implementações das ações padrão
    def _action_select_all(self, context: MenuActionContext) -> Dict[str, Any]:
        """Seleciona todos os pontos visíveis"""
        if not context.view_data:
            return {"error": "No data available"}
        
        # Simula seleção de todos os pontos
        all_indices = list(range(len(context.view_data.t_seconds)))
        
        return {
            "action": "select_points",
            "indices": all_indices,
            "message": f"Selected {len(all_indices)} points"
        }
    
    def _action_select_time_window(self, context: MenuActionContext) -> Dict[str, Any]:
        """Seleciona janela temporal ao redor do clique"""
        if not context.coordinates or not context.view_data:
            return {"error": "No coordinates or data available"}
        
        click_time = context.coordinates[0]
        window_size = 10.0  # 10 segundos de janela
        
        start_time = click_time - window_size / 2
        end_time = click_time + window_size / 2
        
        return {
            "action": "select_time_window",
            "start_time": start_time,
            "end_time": end_time,
            "message": f"Selected window: {start_time:.1f}s - {end_time:.1f}s"
        }
    
    def _action_clear_selection(self, context: MenuActionContext) -> Dict[str, Any]:
        """Limpa seleção atual"""
        self.data_selector.clear_selection()
        
        return {
            "action": "clear_selection",
            "message": "Selection cleared"
        }
    
    def _action_calculate_stats(self, context: MenuActionContext) -> Dict[str, Any]:
        """Calcula estatísticas dos dados selecionados"""
        if not context.has_selection or not context.view_data:
            return {"error": "No selection available"}
        
        selected_indices = context.selected_points
        stats = {}
        
        for series_id, values in context.view_data.series.items():
            if series_id in context.selected_series:
                selected_values = values[selected_indices]
                stats[series_id] = {
                    "count": len(selected_values),
                    "mean": float(selected_values.mean()),
                    "std": float(selected_values.std()),
                    "min": float(selected_values.min()),
                    "max": float(selected_values.max()),
                    "median": float(np.median(selected_values))
                }
        
        return {
            "action": "show_statistics",
            "statistics": stats,
            "message": f"Statistics calculated for {len(stats)} series"
        }
    
    def _action_fit_trend(self, context: MenuActionContext) -> Dict[str, Any]:
        """Ajusta tendência linear aos dados selecionados"""
        if not context.has_selection or not context.view_data:
            return {"error": "No selection available"}
        
        import numpy as np
        
        selected_indices = context.selected_points
        t_selected = context.view_data.t_seconds[selected_indices]
        
        trends = {}
        for series_id in context.selected_series:
            if series_id in context.view_data.series:
                y_selected = context.view_data.series[series_id][selected_indices]
                
                # Fit linear trend
                coeffs = np.polyfit(t_selected, y_selected, 1)
                slope, intercept = coeffs
                
                # Calculate R²
                y_pred = slope * t_selected + intercept
                ss_res = np.sum((y_selected - y_pred) ** 2)
                ss_tot = np.sum((y_selected - np.mean(y_selected)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                trends[series_id] = {
                    "slope": float(slope),
                    "intercept": float(intercept),
                    "r_squared": float(r_squared),
                    "equation": f"y = {slope:.4f}x + {intercept:.4f}"
                }
        
        return {
            "action": "show_trend_analysis",
            "trends": trends,
            "message": f"Trend fitted for {len(trends)} series"
        }
    
    def _action_zoom_to_selection(self, context: MenuActionContext) -> Dict[str, Any]:
        """Zoom para os dados selecionados"""
        if not context.has_selection or not context.view_data:
            return {"error": "No selection available"}
        
        selected_indices = context.selected_points
        t_selected = context.view_data.t_seconds[selected_indices]
        
        # Calcula bounds da seleção
        t_min, t_max = float(t_selected.min()), float(t_selected.max())
        
        # Adiciona margem de 5%
        t_range = t_max - t_min
        margin = t_range * 0.05
        
        return {
            "action": "zoom_to_range",
            "x_range": [t_min - margin, t_max + margin],
            "message": f"Zoomed to selection ({t_min:.1f}s - {t_max:.1f}s)"
        }
    
    def _action_add_annotation(self, context: MenuActionContext) -> Dict[str, Any]:
        """Adiciona anotação no ponto clicado"""
        if not context.coordinates:
            return {"error": "No coordinates available"}
        
        x, y = context.coordinates
        
        return {
            "action": "add_annotation",
            "x": float(x),
            "y": float(y),
            "text": f"Point: ({x:.2f}, {y:.2f})",
            "message": "Annotation added"
        }
    
    def _action_export_selection(self, context: MenuActionContext) -> Dict[str, Any]:
        """Exporta dados selecionados"""
        if not context.has_selection or not context.view_data:
            return {"error": "No selection available"}
        
        selected_indices = context.selected_points
        
        export_data = {
            "timestamps": context.view_data.t_seconds[selected_indices].tolist(),
            "series": {}
        }
        
        for series_id in context.selected_series:
            if series_id in context.view_data.series:
                export_data["series"][series_id] = \
                    context.view_data.series[series_id][selected_indices].tolist()
        
        return {
            "action": "export_data",
            "data": export_data,
            "format": "json",
            "message": f"Exported {len(selected_indices)} points"
        }


# Factory function para facilitar uso
def create_context_menu_manager() -> ContextMenuManager:
    """Cria instância do gerenciador de context menu"""
    return ContextMenuManager()
