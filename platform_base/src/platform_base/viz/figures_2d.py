from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Union

from platform_base.core.models import ViewData, Series
from platform_base.viz.base import BaseFigure, _downsample_lttb
from platform_base.viz.config import VizConfig
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


def _prepare_data_for_plotting(t: np.ndarray, values: np.ndarray, max_points: int = 5000) -> tuple[np.ndarray, np.ndarray]:
    """Prepara dados para plotagem com downsampling inteligente"""
    if len(t) <= max_points:
        return t, values
    
    # Usa LTTB para preservar features importantes
    try:
        t_down, values_down = _downsample_lttb(t, values, max_points)
        logger.debug("lttb_downsampling_applied", 
                    original_points=len(t), 
                    downsampled_points=len(t_down))
        return t_down, values_down
    except Exception as e:
        # Fallback para downsampling uniforme
        logger.warning("lttb_failed_fallback_uniform", error=str(e))
        idx = np.linspace(0, len(t) - 1, max_points).astype(int)
        return t[idx], values[idx]


def _add_interpolated_markers(fig: go.Figure, t: np.ndarray, values: np.ndarray, 
                            is_interpolated: np.ndarray, series_name: str, color: str):
    """Adiciona marcadores para pontos interpolados conforme PRD"""
    if is_interpolated is None or not np.any(is_interpolated):
        return
    
    # Pontos interpolados com marcadores especiais
    interp_indices = np.where(is_interpolated)[0]
    if len(interp_indices) > 0:
        fig.add_trace(
            go.Scatter(
                x=t[interp_indices],
                y=values[interp_indices],
                mode='markers',
                marker=dict(
                    symbol='circle-open',
                    size=6,
                    color=color,
                    line=dict(width=2)
                ),
                name=f"{series_name} (interpolated)",
                hovertemplate="<b>%{fullData.name}</b><br>" +
                            "Time: %{x}<br>" +
                            "Value: %{y}<br>" +
                            "<i>Interpolated point</i><extra></extra>",
                showlegend=False
            )
        )


class TimeseriesPlot(BaseFigure):
    """Plotagem de séries temporais com downsampling inteligente e rastreamento de interpolação"""
    
    def render(self, view_data: ViewData, show_interpolated: bool = True) -> go.Figure:
        """
        Renderiza séries temporais com features avançadas conforme PRD seção 10.1
        
        Args:
            view_data: Dados das séries a serem plotadas
            show_interpolated: Se deve mostrar pontos interpolados
        """
        fig = go.Figure()
        
        # Configurações básicas
        max_points = getattr(self.config.downsample, 'max_points', 5000)
        colors = getattr(self.config.colors, 'palette', 
                        ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        
        for i, (series_id, values) in enumerate(view_data.series.items()):
            # Prepara dados com downsampling inteligente
            t_plot, v_plot = _prepare_data_for_plotting(
                view_data.t_seconds, values, max_points
            )
            
            color = colors[i % len(colors)]
            
            # Adiciona linha principal
            fig.add_trace(
                go.Scatter(
                    x=t_plot,
                    y=v_plot,
                    name=series_id,
                    mode="lines+markers",
                    line=dict(color=color, width=2),
                    marker=dict(size=4, color=color),
                    hovertemplate="<b>%{fullData.name}</b><br>" +
                                "Time: %{x}<br>" +
                                "Value: %{y:.4f}<br>" +
                                "<extra></extra>",
                    connectgaps=False  # Não conecta gaps de dados
                )
            )
            
            # Adiciona marcadores de interpolação se disponível
            if show_interpolated and hasattr(view_data, 'interpolation_mask'):
                interp_mask = view_data.interpolation_mask.get(series_id)
                if interp_mask is not None:
                    _add_interpolated_markers(
                        fig, view_data.t_seconds, values, 
                        interp_mask, series_id, color
                    )
        
        # Layout responsivo e interativo
        fig.update_layout(
            title=dict(
                text=getattr(self.config, 'title', 'Time Series Plot'),
                x=0.5,
                font=dict(size=16)
            ),
            showlegend=getattr(self.config.interactive, 'show_legend', True),
            hovermode=getattr(self.config.interactive, 'hover_mode', 'closest'),
            xaxis=dict(
                title="Time",
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGrey'
            ),
            yaxis=dict(
                title="Value",
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGrey'
            ),
            plot_bgcolor='white',
            # Configurações para seleção de dados
            dragmode='select',
            selectdirection='horizontal',
            # Toolbar customizada
            modebar=dict(
                add=['select2d', 'lasso2d'],
                remove=['autoScale2d']
            )
        )
        
        # Adiciona anotações de metadata se disponível
        if hasattr(view_data, 'metadata') and view_data.metadata:
            fig.add_annotation(
                text=f"Dataset: {view_data.dataset_id}<br>" +
                     f"Points: {len(view_data.t_seconds):,}<br>" +
                     f"Window: {view_data.window.start_seconds:.1f}s - {view_data.window.end_seconds:.1f}s",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                align="left",
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1
            )
        
        return fig


class MultipanelPlot(BaseFigure):
    """Plotagem multipanel com sincronização de eixos conforme PRD seção 10.2"""
    
    def render(self, panels: list[ViewData], shared_xaxes: bool = True, 
              shared_yaxes: bool = False) -> go.Figure:
        """
        Renderiza múltiplos painéis sincronizados
        
        Args:
            panels: Lista de dados para cada painel
            shared_xaxes: Se os eixos X devem ser compartilhados
            shared_yaxes: Se os eixos Y devem ser compartilhados  
        """
        if not panels:
            return go.Figure()
            
        # Cria subplots com configurações avançadas
        subplot_titles = [f"Panel {i+1}" for i in range(len(panels))]
        if hasattr(panels[0], 'metadata'):
            subplot_titles = [panel.metadata.get('title', f'Panel {i+1}') 
                            for i, panel in enumerate(panels)]
        
        fig = make_subplots(
            rows=len(panels), 
            cols=1, 
            shared_xaxes=shared_xaxes,
            shared_yaxes=shared_yaxes,
            subplot_titles=subplot_titles,
            vertical_spacing=0.05,
            specs=[[{"secondary_y": True}] for _ in panels]  # Permite eixo Y duplo
        )
        
        colors = getattr(self.config.colors, 'palette', 
                        ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        max_points = getattr(self.config.downsample, 'max_points', 5000)
        
        for row, panel in enumerate(panels, start=1):
            color_idx = 0
            
            for series_id, values in panel.series.items():
                # Prepara dados
                t_plot, v_plot = _prepare_data_for_plotting(
                    panel.t_seconds, values, max_points
                )
                
                color = colors[color_idx % len(colors)]
                color_idx += 1
                
                # Adiciona trace ao painel específico
                fig.add_trace(
                    go.Scatter(
                        x=t_plot, 
                        y=v_plot, 
                        name=f"{series_id} (P{row})",
                        mode="lines+markers",
                        line=dict(color=color, width=2),
                        marker=dict(size=3, color=color),
                        hovertemplate="<b>%{fullData.name}</b><br>" +
                                    "Time: %{x}<br>" +
                                    "Value: %{y:.4f}<br>" +
                                    f"Panel: {row}<extra></extra>",
                        showlegend=True
                    ),
                    row=row,
                    col=1
                )
        
        # Layout otimizado para multipanel
        fig.update_layout(
            title=dict(
                text=getattr(self.config, 'title', 'Multi-Panel Time Series'),
                x=0.5,
                font=dict(size=16)
            ),
            showlegend=getattr(self.config.interactive, 'show_legend', True),
            hovermode='x unified',  # Hover unificado para comparação
            plot_bgcolor='white',
            height=200 * len(panels) + 100,  # Altura dinâmica
            # Sincronização de zoom
            xaxis=dict(matches='x'),  # Sincroniza zoom X entre painéis
            dragmode='zoom' if shared_xaxes else 'pan'
        )
        
        # Configura eixos individuais
        for i in range(len(panels)):
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGrey',
                row=i+1, col=1
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGrey',
                row=i+1, col=1
            )
        
        return fig


class ScatterPlot(BaseFigure):
    """Plot de dispersão para análise de correlação entre séries"""
    
    def render(self, x_data: ViewData, y_data: ViewData, 
              x_series: str, y_series: str) -> go.Figure:
        """
        Cria scatter plot entre duas séries
        
        Args:
            x_data: Dados para eixo X
            y_data: Dados para eixo Y  
            x_series: ID da série X
            y_series: ID da série Y
        """
        # Extrai dados das séries
        x_values = x_data.series[x_series]
        y_values = y_data.series[y_series]
        
        # Sincroniza timestamps (interpolação simples)
        # TODO: Implementar sincronização mais sofisticada
        min_len = min(len(x_values), len(y_values))
        x_plot = x_values[:min_len]
        y_plot = y_values[:min_len]
        
        # Calcula correlação
        correlation = np.corrcoef(x_plot, y_plot)[0, 1]
        
        fig = go.Figure()
        
        # Scatter principal
        fig.add_trace(
            go.Scatter(
                x=x_plot,
                y=y_plot,
                mode='markers',
                marker=dict(
                    size=6,
                    color=x_data.t_seconds[:min_len],  # Colorir por tempo
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Time")
                ),
                name=f"{x_series} vs {y_series}",
                hovertemplate="<b>%{fullData.name}</b><br>" +
                            f"{x_series}: %{{x:.4f}}<br>" +
                            f"{y_series}: %{{y:.4f}}<br>" +
                            "<extra></extra>"
            )
        )
        
        # Linha de regressão linear
        if len(x_plot) > 1:
            z = np.polyfit(x_plot, y_plot, 1)
            p = np.poly1d(z)
            x_reg = np.linspace(np.min(x_plot), np.max(x_plot), 100)
            y_reg = p(x_reg)
            
            fig.add_trace(
                go.Scatter(
                    x=x_reg,
                    y=y_reg,
                    mode='lines',
                    line=dict(color='red', width=2, dash='dash'),
                    name=f'Linear fit (R²={correlation**2:.3f})',
                    hoverinfo='skip'
                )
            )
        
        fig.update_layout(
            title=f"Scatter Plot: {x_series} vs {y_series}",
            xaxis_title=x_series,
            yaxis_title=y_series,
            showlegend=True,
            plot_bgcolor='white',
            annotations=[
                dict(
                    text=f"Correlation: {correlation:.3f}",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="rgba(0,0,0,0.1)",
                    borderwidth=1
                )
            ]
        )
        
        return fig


class DistributionPlot(BaseFigure):
    """Plot de distribuição (histograma + densidade) conforme PRD seção 10.3"""
    
    def render(self, view_data: ViewData, series_id: str, 
              bins: int = 50, show_kde: bool = True) -> go.Figure:
        """
        Renderiza distribuição de uma série
        
        Args:
            view_data: Dados da série
            series_id: ID da série a analisar
            bins: Número de bins do histograma
            show_kde: Se deve mostrar estimativa de densidade
        """
        values = view_data.series[series_id]
        
        fig = go.Figure()
        
        # Histograma
        fig.add_trace(
            go.Histogram(
                x=values,
                nbinsx=bins,
                name=f"{series_id} distribution",
                opacity=0.7,
                hovertemplate="<b>%{fullData.name}</b><br>" +
                            "Range: %{x}<br>" +
                            "Count: %{y}<br>" +
                            "<extra></extra>"
            )
        )
        
        # Estatísticas básicas
        stats_text = (
            f"Mean: {np.mean(values):.4f}<br>"
            f"Std: {np.std(values):.4f}<br>"
            f"Min: {np.min(values):.4f}<br>"
            f"Max: {np.max(values):.4f}<br>"
            f"Median: {np.median(values):.4f}"
        )
        
        fig.update_layout(
            title=f"Distribution: {series_id}",
            xaxis_title="Value",
            yaxis_title="Frequency",
            showlegend=True,
            plot_bgcolor='white',
            annotations=[
                dict(
                    text=stats_text,
                    xref="paper", yref="paper",
                    x=0.98, y=0.98,
                    showarrow=False,
                    align="right",
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="rgba(0,0,0,0.1)",
                    borderwidth=1
                )
            ]
        )
        
        return fig
