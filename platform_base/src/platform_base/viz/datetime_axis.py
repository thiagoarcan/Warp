"""
DateTimeAxis - Eixo X customizado com formatação de data/hora para pyqtgraph

Features:
- Formatação automática baseada no nível de zoom
- Suporte a múltiplos formatos (ISO, locale, custom)
- Zoom-aware: adapta formato conforme escala
- Sincronização com seleção temporal

Category 2.8 - DateTimeAxis
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt

from platform_base.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = get_logger(__name__)


class DateTimeFormat(Enum):
    """Formatos de exibição de data/hora"""
    ISO = auto()           # 2026-01-31T14:30:00
    LOCALE = auto()        # Formato do sistema
    CUSTOM = auto()        # Formato customizado
    RELATIVE = auto()      # Relativo ao início (00:00:00)


class ZoomLevel(Enum):
    """Níveis de zoom para formatação automática"""
    YEARS = auto()         # > 365 dias visíveis
    MONTHS = auto()        # 30-365 dias
    WEEKS = auto()         # 7-30 dias
    DAYS = auto()          # 1-7 dias
    HOURS = auto()         # 1-24 horas
    MINUTES = auto()       # 1-60 minutos
    SECONDS = auto()       # < 1 minuto
    MILLISECONDS = auto()  # < 1 segundo


# Formatos padrão para cada nível de zoom
ZOOM_FORMATS = {
    ZoomLevel.YEARS: "%Y",
    ZoomLevel.MONTHS: "%Y-%m",
    ZoomLevel.WEEKS: "%Y-%m-%d",
    ZoomLevel.DAYS: "%m-%d",
    ZoomLevel.HOURS: "%d %H:%M",
    ZoomLevel.MINUTES: "%H:%M",
    ZoomLevel.SECONDS: "%H:%M:%S",
    ZoomLevel.MILLISECONDS: "%H:%M:%S.%f",
}


def timestamp_to_datetime(timestamp: float, epoch: datetime | None = None) -> datetime:
    """
    Converte timestamp (segundos) para datetime.
    
    Args:
        timestamp: Segundos desde epoch
        epoch: Datetime de referência (default: Unix epoch)
        
    Returns:
        datetime object
    """
    if epoch is None:
        epoch = datetime(1970, 1, 1)
    return epoch + timedelta(seconds=timestamp)


def datetime_to_timestamp(dt: datetime, epoch: datetime | None = None) -> float:
    """
    Converte datetime para timestamp (segundos).
    
    Args:
        dt: Datetime object
        epoch: Datetime de referência (default: Unix epoch)
        
    Returns:
        Segundos desde epoch
    """
    if epoch is None:
        epoch = datetime(1970, 1, 1)
    return (dt - epoch).total_seconds()


def detect_zoom_level(visible_range: float) -> ZoomLevel:
    """
    Detecta nível de zoom baseado no range visível.
    
    Args:
        visible_range: Range visível em segundos
        
    Returns:
        ZoomLevel apropriado
    """
    if visible_range > 365 * 24 * 3600:  # > 1 ano
        return ZoomLevel.YEARS
    elif visible_range > 30 * 24 * 3600:  # > 1 mês
        return ZoomLevel.MONTHS
    elif visible_range > 7 * 24 * 3600:   # > 1 semana
        return ZoomLevel.WEEKS
    elif visible_range > 24 * 3600:       # > 1 dia
        return ZoomLevel.DAYS
    elif visible_range > 3600:            # > 1 hora
        return ZoomLevel.HOURS
    elif visible_range > 60:              # > 1 minuto
        return ZoomLevel.MINUTES
    elif visible_range > 1:               # > 1 segundo
        return ZoomLevel.SECONDS
    else:
        return ZoomLevel.MILLISECONDS


class DateTimeAxisItem(pg.AxisItem):
    """
    Eixo X customizado para exibição de data/hora.
    
    Automaticamente adapta o formato baseado no nível de zoom.
    """
    
    def __init__(
        self,
        orientation: str = "bottom",
        epoch: datetime | None = None,
        format_mode: DateTimeFormat = DateTimeFormat.ISO,
        custom_format: str | None = None,
        **kwargs
    ):
        """
        Inicializa DateTimeAxisItem.
        
        Args:
            orientation: Orientação do eixo ('bottom', 'top')
            epoch: Datetime de referência para conversão
            format_mode: Modo de formatação
            custom_format: Formato strftime customizado
        """
        super().__init__(orientation, **kwargs)
        
        self._epoch = epoch or datetime(1970, 1, 1)
        self._format_mode = format_mode
        self._custom_format = custom_format
        self._current_zoom_level = ZoomLevel.SECONDS
        
        # Cache para performance
        self._format_cache: dict[float, str] = {}
        self._cache_zoom_level: ZoomLevel | None = None
        
        logger.debug("datetime_axis_created", 
                    epoch=self._epoch.isoformat(),
                    format_mode=format_mode.name)
    
    @property
    def epoch(self) -> datetime:
        """Retorna datetime de referência."""
        return self._epoch
    
    @epoch.setter
    def epoch(self, value: datetime):
        """Define datetime de referência."""
        self._epoch = value
        self._clear_cache()
        self.update()
    
    @property
    def format_mode(self) -> DateTimeFormat:
        """Retorna modo de formatação."""
        return self._format_mode
    
    @format_mode.setter
    def format_mode(self, value: DateTimeFormat):
        """Define modo de formatação."""
        self._format_mode = value
        self._clear_cache()
        self.update()
    
    @property
    def custom_format(self) -> str | None:
        """Retorna formato customizado."""
        return self._custom_format
    
    @custom_format.setter
    def custom_format(self, value: str | None):
        """Define formato customizado."""
        self._custom_format = value
        self._clear_cache()
        self.update()
    
    def _clear_cache(self):
        """Limpa cache de formatação."""
        self._format_cache.clear()
        self._cache_zoom_level = None
    
    def tickStrings(self, values: Sequence[float], scale: float, spacing: float) -> list[str]:
        """
        Gera strings para os ticks do eixo.
        
        Args:
            values: Valores dos ticks (timestamps)
            scale: Escala atual
            spacing: Espaçamento entre ticks
            
        Returns:
            Lista de strings formatadas
        """
        if not values:
            return []
        
        # Detecta nível de zoom baseado no spacing
        visible_range = spacing * 10  # Estimativa do range visível
        zoom_level = detect_zoom_level(visible_range)
        
        # Atualiza cache se nível de zoom mudou
        if zoom_level != self._cache_zoom_level:
            self._clear_cache()
            self._cache_zoom_level = zoom_level
            self._current_zoom_level = zoom_level
        
        # Formata valores
        strings = []
        for value in values:
            strings.append(self._format_timestamp(value, zoom_level))
        
        return strings
    
    def _format_timestamp(self, timestamp: float, zoom_level: ZoomLevel) -> str:
        """
        Formata timestamp para string.
        
        Args:
            timestamp: Timestamp em segundos
            zoom_level: Nível de zoom atual
            
        Returns:
            String formatada
        """
        # Verifica cache
        cache_key = (timestamp, zoom_level)
        if timestamp in self._format_cache:
            return self._format_cache[timestamp]
        
        try:
            dt = timestamp_to_datetime(timestamp, self._epoch)
            
            if self._format_mode == DateTimeFormat.CUSTOM and self._custom_format:
                formatted = dt.strftime(self._custom_format)
            elif self._format_mode == DateTimeFormat.RELATIVE:
                formatted = self._format_relative(timestamp)
            elif self._format_mode == DateTimeFormat.LOCALE:
                formatted = dt.strftime("%x %X")  # Locale format
            else:  # ISO ou default
                fmt = ZOOM_FORMATS.get(zoom_level, "%H:%M:%S")
                formatted = dt.strftime(fmt)
            
            # Cache result
            self._format_cache[timestamp] = formatted
            return formatted
            
        except (ValueError, OverflowError) as e:
            logger.warning("timestamp_format_error", timestamp=timestamp, error=str(e))
            return f"{timestamp:.2f}"
    
    def _format_relative(self, timestamp: float) -> str:
        """
        Formata timestamp como tempo relativo (HH:MM:SS.mmm).
        
        Args:
            timestamp: Timestamp em segundos desde epoch
            
        Returns:
            String no formato HH:MM:SS.mmm
        """
        if timestamp < 0:
            sign = "-"
            timestamp = abs(timestamp)
        else:
            sign = ""
        
        hours = int(timestamp // 3600)
        minutes = int((timestamp % 3600) // 60)
        seconds = timestamp % 60
        
        if hours > 0:
            return f"{sign}{hours:02d}:{minutes:02d}:{seconds:05.2f}"
        elif minutes > 0:
            return f"{sign}{minutes:02d}:{seconds:05.2f}"
        else:
            return f"{sign}{seconds:.3f}s"
    
    def tickValues(self, minVal: float, maxVal: float, size: int) -> list[tuple[float, list[float]]]:
        """
        Gera valores dos ticks baseado no range.
        
        Args:
            minVal: Valor mínimo do range
            maxVal: Valor máximo do range
            size: Tamanho do eixo em pixels
            
        Returns:
            Lista de tuplas (spacing, [tick_values])
        """
        # Detecta nível de zoom
        visible_range = maxVal - minVal
        zoom_level = detect_zoom_level(visible_range)
        
        # Define espaçamento baseado no nível de zoom
        spacing = self._get_tick_spacing(zoom_level, visible_range)
        
        # Gera ticks
        ticks = self._generate_ticks(minVal, maxVal, spacing)
        
        return [(spacing, ticks)]
    
    def _get_tick_spacing(self, zoom_level: ZoomLevel, visible_range: float) -> float:
        """
        Calcula espaçamento entre ticks baseado no zoom.
        
        Args:
            zoom_level: Nível de zoom atual
            visible_range: Range visível em segundos
            
        Returns:
            Espaçamento em segundos
        """
        # Espaçamentos "bonitos" para cada nível
        spacing_map = {
            ZoomLevel.YEARS: 365 * 24 * 3600,      # 1 ano
            ZoomLevel.MONTHS: 30 * 24 * 3600,      # 1 mês
            ZoomLevel.WEEKS: 7 * 24 * 3600,        # 1 semana
            ZoomLevel.DAYS: 24 * 3600,             # 1 dia
            ZoomLevel.HOURS: 3600,                 # 1 hora
            ZoomLevel.MINUTES: 60,                 # 1 minuto
            ZoomLevel.SECONDS: 1,                  # 1 segundo
            ZoomLevel.MILLISECONDS: 0.1,           # 100ms
        }
        
        base_spacing = spacing_map.get(zoom_level, 1)
        
        # Ajusta para ter ~5-10 ticks visíveis
        target_ticks = 7
        actual_ticks = visible_range / base_spacing
        
        if actual_ticks > 15:
            # Muito ticks, aumenta espaçamento
            multipliers = [1, 2, 5, 10, 15, 30, 60]
            for mult in multipliers:
                if visible_range / (base_spacing * mult) <= 15:
                    return base_spacing * mult
            return base_spacing * 60
        elif actual_ticks < 3:
            # Poucos ticks, diminui espaçamento
            divisors = [2, 5, 10]
            for div in divisors:
                if visible_range / (base_spacing / div) >= 3:
                    return base_spacing / div
            return base_spacing / 10
        
        return base_spacing
    
    def _generate_ticks(self, minVal: float, maxVal: float, spacing: float) -> list[float]:
        """
        Gera valores de ticks no range especificado.
        
        Args:
            minVal: Valor mínimo
            maxVal: Valor máximo
            spacing: Espaçamento entre ticks
            
        Returns:
            Lista de valores de ticks
        """
        if spacing <= 0:
            return []
        
        # Alinha primeiro tick com o espaçamento
        first_tick = np.ceil(minVal / spacing) * spacing
        last_tick = np.floor(maxVal / spacing) * spacing
        
        # Gera ticks
        n_ticks = int((last_tick - first_tick) / spacing) + 1
        n_ticks = min(n_ticks, 100)  # Limita para evitar memory issues
        
        ticks = [first_tick + i * spacing for i in range(n_ticks)]
        
        return ticks


class DateTimePlotWidget(pg.PlotWidget):
    """
    PlotWidget com eixo X de data/hora integrado.
    
    Wrapper conveniente para criar plots com DateTimeAxisItem.
    """
    
    def __init__(
        self,
        epoch: datetime | None = None,
        format_mode: DateTimeFormat = DateTimeFormat.ISO,
        custom_format: str | None = None,
        **kwargs
    ):
        """
        Inicializa DateTimePlotWidget.
        
        Args:
            epoch: Datetime de referência
            format_mode: Modo de formatação do eixo X
            custom_format: Formato strftime customizado
            **kwargs: Argumentos adicionais para PlotWidget
        """
        # Cria eixo customizado
        self._datetime_axis = DateTimeAxisItem(
            orientation="bottom",
            epoch=epoch,
            format_mode=format_mode,
            custom_format=custom_format,
        )
        
        # Inicializa PlotWidget com eixo customizado
        super().__init__(axisItems={"bottom": self._datetime_axis}, **kwargs)
        
        # Configurações adicionais
        self.setLabel("bottom", "Time")
        
        logger.debug("datetime_plot_widget_created")
    
    @property
    def datetime_axis(self) -> DateTimeAxisItem:
        """Retorna o eixo de data/hora."""
        return self._datetime_axis
    
    def set_epoch(self, epoch: datetime):
        """Define datetime de referência."""
        self._datetime_axis.epoch = epoch
    
    def set_format_mode(self, mode: DateTimeFormat):
        """Define modo de formatação."""
        self._datetime_axis.format_mode = mode
    
    def set_custom_format(self, fmt: str | None):
        """Define formato customizado."""
        self._datetime_axis.custom_format = fmt
    
    def plot_with_datetime(
        self,
        datetimes: Sequence[datetime],
        values: Sequence[float],
        **kwargs
    ):
        """
        Plota dados com datetimes no eixo X.
        
        Args:
            datetimes: Sequência de datetimes
            values: Valores correspondentes
            **kwargs: Argumentos adicionais para plot()
            
        Returns:
            PlotDataItem criado
        """
        # Converte datetimes para timestamps
        epoch = self._datetime_axis.epoch
        timestamps = [datetime_to_timestamp(dt, epoch) for dt in datetimes]
        
        return self.plot(timestamps, values, **kwargs)


# Convenience function
def create_datetime_plot(
    epoch: datetime | None = None,
    format_mode: DateTimeFormat = DateTimeFormat.ISO,
    **kwargs
) -> DateTimePlotWidget:
    """
    Cria um DateTimePlotWidget configurado.
    
    Args:
        epoch: Datetime de referência
        format_mode: Modo de formatação
        **kwargs: Argumentos adicionais
        
    Returns:
        DateTimePlotWidget configurado
    """
    return DateTimePlotWidget(
        epoch=epoch,
        format_mode=format_mode,
        **kwargs
    )


__all__ = [
    "DateTimeAxisItem",
    "DateTimeFormat",
    "DateTimePlotWidget",
    "ZoomLevel",
    "create_datetime_plot",
    "datetime_to_timestamp",
    "detect_zoom_level",
    "timestamp_to_datetime",
]
