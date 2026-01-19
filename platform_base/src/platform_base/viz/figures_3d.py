from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Union, Tuple

from platform_base.core.models import ViewData
from platform_base.viz.base import BaseFigure, _downsample_lttb
from platform_base.viz.config import VizConfig
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


class Trajectory3D(BaseFigure):
    """Visualização 3D de trajetórias temporais conforme PRD seção 10.4"""
    
    def render(self, x_data: ViewData, y_data: ViewData, z_data: ViewData,
               x_series: str, y_series: str, z_series: str,
               color_by_time: bool = True) -> go.Figure:
        """
        Renderiza trajetória 3D de três séries temporais
        
        Args:
            x_data, y_data, z_data: Dados das três dimensões
            x_series, y_series, z_series: IDs das séries para X, Y, Z
            color_by_time: Se deve colorir por tempo
        """
        # Extrai dados das séries
        x_values = x_data.series[x_series]
        y_values = y_data.series[y_series] 
        z_values = z_data.series[z_series]
        
        # Sincroniza dados (usa menor comprimento)
        min_len = min(len(x_values), len(y_values), len(z_values))
        x_plot = x_values[:min_len]
        y_plot = y_values[:min_len]
        z_plot = z_values[:min_len]
        t_plot = x_data.t_seconds[:min_len]
        
        # Downsampling se necessário
        max_points = getattr(self.config.downsample, 'max_points', 5000)
        if len(x_plot) > max_points:
            # Downsampling uniforme para manter sincronização 3D
            indices = np.linspace(0, len(x_plot)-1, max_points).astype(int)
            x_plot = x_plot[indices]
            y_plot = y_plot[indices]
            z_plot = z_plot[indices]
            t_plot = t_plot[indices]
        
        fig = go.Figure()
        
        # Trajetória principal
        if color_by_time:
            # Colorir por tempo
            fig.add_trace(
                go.Scatter3d(
                    x=x_plot,
                    y=y_plot,
                    z=z_plot,
                    mode='lines+markers',
                    line=dict(
                        color=t_plot,
                        colorscale='Viridis',
                        width=4,
                        showscale=True,
                        colorbar=dict(title="Time")
                    ),
                    marker=dict(
                        size=3,
                        color=t_plot,
                        colorscale='Viridis'
                    ),
                    name="Trajectory",
                    hovertemplate="<b>3D Trajectory</b><br>" +
                                f"{x_series}: %{{x:.4f}}<br>" +
                                f"{y_series}: %{{y:.4f}}<br>" +
                                f"{z_series}: %{{z:.4f}}<br>" +
                                "Time: %{text}<br>" +
                                "<extra></extra>",
                    text=t_plot
                )
            )
        else:
            fig.add_trace(
                go.Scatter3d(
                    x=x_plot,
                    y=y_plot,
                    z=z_plot,
                    mode='lines+markers',
                    line=dict(color='blue', width=4),
                    marker=dict(size=3, color='blue'),
                    name="Trajectory",
                    hovertemplate="<b>3D Trajectory</b><br>" +
                                f"{x_series}: %{{x:.4f}}<br>" +
                                f"{y_series}: %{{y:.4f}}<br>" +
                                f"{z_series}: %{{z:.4f}}<br>" +
                                "<extra></extra>"
                )
            )
        
        # Marcadores de início e fim
        fig.add_trace(
            go.Scatter3d(
                x=[x_plot[0]],
                y=[y_plot[0]],
                z=[z_plot[0]],
                mode='markers',
                marker=dict(size=10, color='green', symbol='circle'),
                name="Start",
                hovertemplate="<b>Start Point</b><br>" +
                            f"{x_series}: %{{x:.4f}}<br>" +
                            f"{y_series}: %{{y:.4f}}<br>" +
                            f"{z_series}: %{{z:.4f}}<br>" +
                            "<extra></extra>"
            )
        )
        
        fig.add_trace(
            go.Scatter3d(
                x=[x_plot[-1]],
                y=[y_plot[-1]],
                z=[z_plot[-1]],
                mode='markers',
                marker=dict(size=10, color='red', symbol='circle'),
                name="End",
                hovertemplate="<b>End Point</b><br>" +
                            f"{x_series}: %{{x:.4f}}<br>" +
                            f"{y_series}: %{{y:.4f}}<br>" +
                            f"{z_series}: %{{z:.4f}}<br>" +
                            "<extra></extra>"
            )
        )
        
        # Layout 3D otimizado
        fig.update_layout(
            title=dict(
                text=f"3D Trajectory: {x_series}, {y_series}, {z_series}",
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis_title=x_series,
                yaxis_title=y_series,
                zaxis_title=z_series,
                aspectmode='cube',  # Mantém proporções
                camera=dict(
                    eye=dict(x=1.2, y=1.2, z=1.2)  # Posição inicial da câmera
                )
            ),
            showlegend=True,
            hovermode='closest'
        )
        
        return fig


class Surface3D(BaseFigure):
    """Visualização 3D de superfície para análise temporal de múltiplas séries"""
    
    def render(self, view_data: ViewData, z_axis: str = 'series') -> go.Figure:
        """
        Cria superfície 3D com tempo, séries e valores
        
        Args:
            view_data: Dados das séries
            z_axis: 'series' para séries como Z, 'time' para tempo como Z
        """
        # Prepara dados para superfície
        series_ids = list(view_data.series.keys())
        t_seconds = view_data.t_seconds
        
        # Cria mesh grid
        if z_axis == 'series':
            # X = tempo, Y = série index, Z = valor
            X, Y = np.meshgrid(t_seconds, range(len(series_ids)))
            Z = np.array([view_data.series[sid] for sid in series_ids])
            
            x_title = "Time"
            y_title = "Series Index"
            z_title = "Value"
            
        else:  # z_axis == 'time'
            # X = série index, Y = valor, Z = tempo  
            # Esta configuração é mais experimental
            X, Z = np.meshgrid(range(len(series_ids)), t_seconds)
            Y = np.array([view_data.series[sid] for sid in series_ids]).T
            
            x_title = "Series Index"
            y_title = "Value"
            z_title = "Time"
        
        fig = go.Figure()
        
        # Superfície principal
        fig.add_trace(
            go.Surface(
                x=X,
                y=Y, 
                z=Z,
                colorscale='Viridis',
                opacity=0.8,
                name="Data Surface",
                hovertemplate="<b>Data Surface</b><br>" +
                            f"{x_title}: %{{x:.2f}}<br>" +
                            f"{y_title}: %{{y:.2f}}<br>" +
                            f"{z_title}: %{{z:.4f}}<br>" +
                            "<extra></extra>"
            )
        )
        
        # Adiciona contornos na base (projeção)
        fig.add_trace(
            go.Contour(
                x=t_seconds,
                y=range(len(series_ids)),
                z=Z,
                colorscale='Viridis',
                opacity=0.6,
                name="Projection",
                showscale=False,
                contours=dict(
                    z=dict(
                        show=True,
                        usecolormap=True,
                        project=dict(z=True)
                    )
                ),
                hoverinfo='skip'
            )
        )
        
        fig.update_layout(
            title=dict(
                text="3D Surface View - Multi-Series Data",
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis_title=x_title,
                yaxis_title=y_title,
                zaxis_title=z_title,
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            showlegend=True
        )
        
        return fig


class VolumetricPlot(BaseFigure):
    """Visualização volumétrica para análise de densidade de dados"""
    
    def render(self, x_data: ViewData, y_data: ViewData, z_data: ViewData,
               x_series: str, y_series: str, z_series: str,
               bins: int = 20) -> go.Figure:
        """
        Cria visualização volumétrica com densidade de pontos
        
        Args:
            x_data, y_data, z_data: Dados das três dimensões
            x_series, y_series, z_series: IDs das séries
            bins: Resolução da grade volumétrica
        """
        # Extrai e sincroniza dados
        x_values = x_data.series[x_series]
        y_values = y_data.series[y_series]
        z_values = z_data.series[z_series]
        
        min_len = min(len(x_values), len(y_values), len(z_values))
        x_plot = x_values[:min_len]
        y_plot = y_values[:min_len]
        z_plot = z_values[:min_len]
        
        # Cria histograma 3D (densidade)
        hist, edges = np.histogramdd([x_plot, y_plot, z_plot], bins=bins)
        
        # Coordenadas dos centros dos bins
        x_centers = (edges[0][:-1] + edges[0][1:]) / 2
        y_centers = (edges[1][:-1] + edges[1][1:]) / 2  
        z_centers = (edges[2][:-1] + edges[2][1:]) / 2
        
        # Encontra bins não vazios
        x_mesh, y_mesh, z_mesh = np.meshgrid(x_centers, y_centers, z_centers, indexing='ij')
        
        # Flattening para plotagem
        x_flat = x_mesh.flatten()
        y_flat = y_mesh.flatten()
        z_flat = z_mesh.flatten()
        density_flat = hist.flatten()
        
        # Remove pontos com densidade zero
        mask = density_flat > 0
        x_plot_vol = x_flat[mask]
        y_plot_vol = y_flat[mask]
        z_plot_vol = z_flat[mask]
        density_plot = density_flat[mask]
        
        fig = go.Figure()
        
        # Scatter 3D com tamanho baseado na densidade
        fig.add_trace(
            go.Scatter3d(
                x=x_plot_vol,
                y=y_plot_vol,
                z=z_plot_vol,
                mode='markers',
                marker=dict(
                    size=density_plot / np.max(density_plot) * 20,  # Normaliza tamanho
                    color=density_plot,
                    colorscale='Hot',
                    opacity=0.6,
                    showscale=True,
                    colorbar=dict(title="Density")
                ),
                name="Data Density",
                hovertemplate="<b>Volume Density</b><br>" +
                            f"{x_series}: %{{x:.4f}}<br>" +
                            f"{y_series}: %{{y:.4f}}<br>" +
                            f"{z_series}: %{{z:.4f}}<br>" +
                            "Density: %{text}<br>" +
                            "<extra></extra>",
                text=density_plot
            )
        )
        
        fig.update_layout(
            title=dict(
                text=f"Volumetric View: {x_series}, {y_series}, {z_series}",
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis_title=x_series,
                yaxis_title=y_series,
                zaxis_title=z_series,
                camera=dict(
                    eye=dict(x=1.2, y=1.2, z=1.2)
                )
            ),
            showlegend=True
        )
        
        return fig


class StateSpacePlot(BaseFigure):
    """Visualização de espaço de estados para análise dinâmica"""
    
    def render(self, view_data: ViewData, series_id: str, 
               lag: int = 1, dimensions: int = 3) -> go.Figure:
        """
        Cria plot de espaço de estados usando embedding de atraso
        
        Args:
            view_data: Dados da série
            series_id: ID da série a analisar
            lag: Atraso para embedding
            dimensions: Número de dimensões (2 ou 3)
        """
        values = view_data.series[series_id]
        
        if len(values) < lag * dimensions:
            raise ValueError("Série muito curta para embedding especificado")
        
        # Cria embedding de atraso
        embedded = []
        for i in range(dimensions):
            start_idx = i * lag
            end_idx = len(values) - (dimensions - i - 1) * lag
            embedded.append(values[start_idx:end_idx])
        
        embedded = np.array(embedded).T
        
        fig = go.Figure()
        
        if dimensions == 2:
            # Plot 2D
            fig.add_trace(
                go.Scatter(
                    x=embedded[:, 0],
                    y=embedded[:, 1],
                    mode='lines+markers',
                    line=dict(color='blue', width=2),
                    marker=dict(size=4, color='blue'),
                    name=f"State Space (lag={lag})",
                    hovertemplate="<b>State Space</b><br>" +
                                f"x(t): %{{x:.4f}}<br>" +
                                f"x(t-{lag}): %{{y:.4f}}<br>" +
                                "<extra></extra>"
                )
            )
            
            fig.update_layout(
                title=f"State Space Plot: {series_id} (2D, lag={lag})",
                xaxis_title=f"x(t)",
                yaxis_title=f"x(t-{lag})",
                showlegend=True
            )
            
        else:  # dimensions == 3
            # Plot 3D
            colors = np.arange(len(embedded))
            
            fig.add_trace(
                go.Scatter3d(
                    x=embedded[:, 0],
                    y=embedded[:, 1],
                    z=embedded[:, 2],
                    mode='lines+markers',
                    line=dict(
                        color=colors,
                        colorscale='Viridis',
                        width=4,
                        showscale=True,
                        colorbar=dict(title="Time Index")
                    ),
                    marker=dict(
                        size=3,
                        color=colors,
                        colorscale='Viridis'
                    ),
                    name=f"State Space (lag={lag})",
                    hovertemplate="<b>State Space</b><br>" +
                                f"x(t): %{{x:.4f}}<br>" +
                                f"x(t-{lag}): %{{y:.4f}}<br>" +
                                f"x(t-{2*lag}): %{{z:.4f}}<br>" +
                                "<extra></extra>"
                )
            )
            
            fig.update_layout(
                title=f"State Space Plot: {series_id} (3D, lag={lag})",
                scene=dict(
                    xaxis_title=f"x(t)",
                    yaxis_title=f"x(t-{lag})",
                    zaxis_title=f"x(t-{2*lag})",
                    camera=dict(
                        eye=dict(x=1.2, y=1.2, z=1.2)
                    )
                ),
                showlegend=True
            )
        
        return fig
