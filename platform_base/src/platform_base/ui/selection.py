from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

import numpy as np

from platform_base.core.models import Dataset, TimeWindow, ViewData
from platform_base.utils.logging import get_logger


if TYPE_CHECKING:
    from collections.abc import Callable


logger = get_logger(__name__)


class SelectionMode(Enum):
    """Modos de seleção conforme PRD seção 13"""
    TEMPORAL = "temporal"           # Seleção por janela temporal
    INTERACTIVE = "interactive"     # Seleção via interface gráfica
    CONDITIONAL = "conditional"     # Seleção por condições/predicados


@dataclass
class SelectionCriteria:
    """Critérios de seleção unificados"""
    mode: SelectionMode

    # Seleção temporal
    start_time: float | None = None
    end_time: float | None = None

    # Seleção interativa
    selected_points: list[int] | None = None
    selected_ranges: list[tuple] | None = None

    # Seleção condicional
    series_id: str | None = None
    condition: str | None = None  # String de condição (ex: "> 10", "< mean + 2*std")
    predicate: Callable | None = None  # Função de predicado customizada

    # Metadados
    description: str = ""
    timestamp: float | None = None


@dataclass
class Selection:
    """Resultado de uma seleção de dados"""
    t_seconds: np.ndarray
    series: dict[str, np.ndarray]
    criteria: SelectionCriteria
    metadata: dict[str, Any]

    @property
    def n_points(self) -> int:
        """Número de pontos selecionados"""
        return len(self.t_seconds)

    @property
    def series_ids(self) -> list[str]:
        """IDs das séries incluídas na seleção"""
        return list(self.series.keys())

    def to_view_data(self, dataset_id: str) -> ViewData:
        """
        Converte seleção para ViewData

        Args:
            dataset_id: ID do dataset

        Returns:
            ViewData com séries selecionadas e janela temporal

        Note:
            O campo t_datetime será None se:
            - Não houver referência temporal em metadata['t_reference']
            - A conversão falhar por qualquer motivo
            Callers devem verificar se t_datetime é None antes de usar.
        """
        import pandas as pd

        # Convert t_seconds to datetime if we have a time reference in metadata
        t_datetime = None
        if "t_reference" in self.metadata and self.metadata["t_reference"] is not None:
            try:
                # Convert reference time to pandas Timestamp and add seconds offset
                t_datetime = pd.to_datetime(self.metadata["t_reference"]) + pd.to_timedelta(self.t_seconds, unit="s")
            except Exception as e:
                logger.warning("datetime_conversion_failed", error=str(e))
                t_datetime = None

        return ViewData(
            dataset_id=dataset_id,
            series=self.series,
            t_seconds=self.t_seconds,
            t_datetime=t_datetime,
            window=TimeWindow(
                start_seconds=float(np.min(self.t_seconds)),
                end_seconds=float(np.max(self.t_seconds)),
            ),
        )


class DataSelector:
    """
    Sistema unificado de seleção de dados conforme PRD seção 13

    Suporta três tipos de seleção:
    1. Temporal - por janelas de tempo
    2. Interativa - via interface gráfica (cliques, lasso, etc)
    3. Condicional - por predicados e condições
    """

    def __init__(self):
        self.active_selection: Selection | None = None
        self.selection_history: list[Selection] = []

    def select_temporal(self, dataset: Dataset, start_seconds: float,
                       end_seconds: float, series_ids: list[str] | None = None) -> Selection:
        """
        Seleção por janela temporal conforme PRD seção 13.1

        Args:
            dataset: Dataset fonte
            start_seconds: Tempo inicial da seleção
            end_seconds: Tempo final da seleção
            series_ids: Lista de séries a incluir (None = todas)
        """
        logger.debug("temporal_selection_start",
                    start=start_seconds, end=end_seconds,
                    n_series=len(series_ids) if series_ids else len(dataset.series))

        # Valida inputs
        if start_seconds >= end_seconds:
            raise ValueError("start_seconds deve ser menor que end_seconds")

        # Cria máscara temporal
        mask = (dataset.t_seconds >= start_seconds) & (dataset.t_seconds <= end_seconds)

        if not np.any(mask):
            logger.warning("temporal_selection_empty", start=start_seconds, end=end_seconds)
            return self._create_empty_selection(SelectionMode.TEMPORAL)

        # Seleciona séries
        target_series = series_ids if series_ids else list(dataset.series.keys())
        selected_series = {}

        for series_id in target_series:
            if series_id in dataset.series:
                selected_series[series_id] = dataset.series[series_id].values[mask]

        criteria = SelectionCriteria(
            mode=SelectionMode.TEMPORAL,
            start_time=start_seconds,
            end_time=end_seconds,
            description=f"Temporal selection: {start_seconds:.2f}s - {end_seconds:.2f}s",
        )

        selection = Selection(
            t_seconds=dataset.t_seconds[mask],
            series=selected_series,
            criteria=criteria,
            metadata={
                "original_points": len(dataset.t_seconds),
                "selected_points": np.sum(mask),
                "selection_ratio": np.sum(mask) / len(dataset.t_seconds),
            },
        )

        self._register_selection(selection)

        logger.info("temporal_selection_complete",
                   points_selected=selection.n_points,
                   series_count=len(selected_series))

        return selection

    def select_interactive(self, dataset: Dataset, selected_points: list[int],
                          series_ids: list[str] | None = None) -> Selection:
        """
        Seleção interativa por índices de pontos conforme PRD seção 13.2

        Args:
            dataset: Dataset fonte
            selected_points: Lista de índices selecionados
            series_ids: Lista de séries a incluir (None = todas)
        """
        logger.debug("interactive_selection_start",
                    point_count=len(selected_points),
                    n_series=len(series_ids) if series_ids else len(dataset.series))

        if not selected_points:
            return self._create_empty_selection(SelectionMode.INTERACTIVE)

        # Valida índices
        max_idx = len(dataset.t_seconds) - 1
        valid_points = [p for p in selected_points if 0 <= p <= max_idx]

        if len(valid_points) != len(selected_points):
            logger.warning("interactive_selection_invalid_indices",
                          removed=len(selected_points) - len(valid_points))

        if not valid_points:
            return self._create_empty_selection(SelectionMode.INTERACTIVE)

        # Ordena índices para manter ordem temporal
        valid_points = sorted(valid_points)

        # Seleciona dados
        target_series = series_ids if series_ids else list(dataset.series.keys())
        selected_series = {}

        for series_id in target_series:
            if series_id in dataset.series:
                selected_series[series_id] = dataset.series[series_id].values[valid_points]

        criteria = SelectionCriteria(
            mode=SelectionMode.INTERACTIVE,
            selected_points=valid_points,
            description=f"Interactive selection: {len(valid_points)} points",
        )

        selection = Selection(
            t_seconds=dataset.t_seconds[valid_points],
            series=selected_series,
            criteria=criteria,
            metadata={
                "original_points": len(dataset.t_seconds),
                "selected_points": len(valid_points),
                "selection_method": "point_indices",
            },
        )

        self._register_selection(selection)

        logger.info("interactive_selection_complete",
                   points_selected=selection.n_points)

        return selection

    def select_interactive_ranges(self, dataset: Dataset, time_ranges: list[tuple],
                                series_ids: list[str] | None = None) -> Selection:
        """
        Seleção interativa por ranges temporais (ex: lasso selection)

        Args:
            dataset: Dataset fonte
            time_ranges: Lista de (start, end) ranges
            series_ids: Lista de séries a incluir
        """
        logger.debug("interactive_ranges_selection_start",
                    range_count=len(time_ranges))

        if not time_ranges:
            return self._create_empty_selection(SelectionMode.INTERACTIVE)

        # Combina todas as ranges em uma máscara
        combined_mask = np.zeros(len(dataset.t_seconds), dtype=bool)

        for start_time, end_time in time_ranges:
            if start_time >= end_time:
                logger.warning("invalid_time_range", start=start_time, end=end_time)
                continue

            range_mask = (dataset.t_seconds >= start_time) & (dataset.t_seconds <= end_time)
            combined_mask |= range_mask

        if not np.any(combined_mask):
            return self._create_empty_selection(SelectionMode.INTERACTIVE)

        # Seleciona dados
        target_series = series_ids if series_ids else list(dataset.series.keys())
        selected_series = {}

        for series_id in target_series:
            if series_id in dataset.series:
                selected_series[series_id] = dataset.series[series_id].values[combined_mask]

        criteria = SelectionCriteria(
            mode=SelectionMode.INTERACTIVE,
            selected_ranges=time_ranges,
            description=f"Interactive ranges: {len(time_ranges)} ranges",
        )

        selection = Selection(
            t_seconds=dataset.t_seconds[combined_mask],
            series=selected_series,
            criteria=criteria,
            metadata={
                "original_points": len(dataset.t_seconds),
                "selected_points": np.sum(combined_mask),
                "range_count": len(time_ranges),
                "selection_method": "time_ranges",
            },
        )

        self._register_selection(selection)

        return selection

    def select_conditional(self, dataset: Dataset, series_id: str,
                          condition: str, series_ids: list[str] | None = None) -> Selection:
        """
        Seleção condicional por predicados conforme PRD seção 13.3

        Args:
            dataset: Dataset fonte
            series_id: ID da série para aplicar condição
            condition: String de condição (ex: "> 10", "< mean + 2*std")
            series_ids: Lista de séries a incluir na seleção

        Condições suportadas:
        - Operadores: >, <, >=, <=, ==, !=
        - Estatísticas: mean, std, median, min, max
        - Exemplos: "> 10", "< mean + 2*std", ">= median", "!= 0"
        """
        logger.debug("conditional_selection_start",
                    series_id=series_id, condition=condition)

        if series_id not in dataset.series:
            raise ValueError(f"Série '{series_id}' não encontrada no dataset")

        # Obtém dados da série de referência
        ref_values = dataset.series[series_id].values

        # Avalia condição
        try:
            mask = self._evaluate_condition(ref_values, condition)
        except Exception as e:
            logger.exception("conditional_selection_failed",
                        condition=condition, error=str(e))
            raise ValueError(f"Erro ao avaliar condição '{condition}': {e}")

        if not np.any(mask):
            logger.warning("conditional_selection_empty",
                          condition=condition, series_id=series_id)
            return self._create_empty_selection(SelectionMode.CONDITIONAL)

        # Seleciona dados
        target_series = series_ids if series_ids else list(dataset.series.keys())
        selected_series = {}

        for sid in target_series:
            if sid in dataset.series:
                selected_series[sid] = dataset.series[sid].values[mask]

        criteria = SelectionCriteria(
            mode=SelectionMode.CONDITIONAL,
            series_id=series_id,
            condition=condition,
            description=f"Conditional: {series_id} {condition}",
        )

        selection = Selection(
            t_seconds=dataset.t_seconds[mask],
            series=selected_series,
            criteria=criteria,
            metadata={
                "original_points": len(dataset.t_seconds),
                "selected_points": np.sum(mask),
                "condition_series": series_id,
                "condition_string": condition,
            },
        )

        self._register_selection(selection)

        logger.info("conditional_selection_complete",
                   points_selected=selection.n_points,
                   condition=condition)

        return selection

    def select_by_predicate(self, dataset: Dataset, predicate: Callable[[np.ndarray], np.ndarray],
                           series_id: str, description: str = "",
                           series_ids: list[str] | None = None) -> Selection:
        """
        Seleção por função de predicado customizada

        Args:
            dataset: Dataset fonte
            predicate: Função que retorna máscara booleana
            series_id: ID da série para aplicar predicado
            description: Descrição da seleção
            series_ids: Lista de séries a incluir
        """
        logger.debug("predicate_selection_start",
                    series_id=series_id, description=description)

        if series_id not in dataset.series:
            raise ValueError(f"Série '{series_id}' não encontrada no dataset")

        ref_values = dataset.series[series_id].values

        try:
            mask = predicate(ref_values)
            if not isinstance(mask, np.ndarray) or mask.dtype != bool:
                raise ValueError("Predicado deve retornar array booleano")
            if len(mask) != len(ref_values):
                raise ValueError("Tamanho da máscara deve ser igual ao da série")
        except Exception as e:
            logger.exception("predicate_selection_failed", error=str(e))
            raise ValueError(f"Erro no predicado: {e}")

        if not np.any(mask):
            return self._create_empty_selection(SelectionMode.CONDITIONAL)

        # Seleciona dados
        target_series = series_ids if series_ids else list(dataset.series.keys())
        selected_series = {}

        for sid in target_series:
            if sid in dataset.series:
                selected_series[sid] = dataset.series[sid].values[mask]

        criteria = SelectionCriteria(
            mode=SelectionMode.CONDITIONAL,
            series_id=series_id,
            predicate=predicate,
            description=description or f"Custom predicate on {series_id}",
        )

        selection = Selection(
            t_seconds=dataset.t_seconds[mask],
            series=selected_series,
            criteria=criteria,
            metadata={
                "original_points": len(dataset.t_seconds),
                "selected_points": np.sum(mask),
                "predicate_series": series_id,
            },
        )

        self._register_selection(selection)

        return selection

    def _evaluate_condition(self, values: np.ndarray, condition: str) -> np.ndarray:
        """Avalia string de condição e retorna máscara booleana"""
        # Calcula estatísticas básicas
        stats = {
            "mean": np.mean(values),
            "std": np.std(values),
            "median": np.median(values),
            "min": np.min(values),
            "max": np.max(values),
        }

        # Substitui estatísticas na condição
        condition_eval = condition
        for stat_name, stat_value in stats.items():
            condition_eval = condition_eval.replace(stat_name, str(stat_value))

        # Parse e avalia condição
        condition_eval = condition_eval.strip()

        # Operadores suportados
        operators = [">=", "<=", ">", "<", "==", "!="]

        for op in operators:
            if op in condition_eval:
                parts = condition_eval.split(op, 1)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()

                    # Left side deve estar vazio (operação unária) ou ser 'values'
                    if left in {"", "values"}:
                        try:
                            threshold = float(eval(right, {"__builtins__": {}}, stats))
                            if op == ">":
                                return values > threshold
                            if op == "<":
                                return values < threshold
                            if op == ">=":
                                return values >= threshold
                            if op == "<=":
                                return values <= threshold
                            if op == "==":
                                return np.isclose(values, threshold)
                            if op == "!=":
                                return ~np.isclose(values, threshold)
                        except Exception:
                            pass
                break

        raise ValueError(f"Condição inválida: {condition}")

    def _create_empty_selection(self, mode: SelectionMode) -> Selection:
        """Cria seleção vazia"""
        criteria = SelectionCriteria(
            mode=mode,
            description="Empty selection",
        )

        return Selection(
            t_seconds=np.array([]),
            series={},
            criteria=criteria,
            metadata={"selected_points": 0, "empty": True},
        )

    def _register_selection(self, selection: Selection):
        """Registra seleção no histórico"""
        import time
        selection.criteria.timestamp = time.time()
        self.active_selection = selection
        self.selection_history.append(selection)

        # Mantém histórico limitado
        if len(self.selection_history) > 100:
            self.selection_history = self.selection_history[-100:]

    def get_selection_history(self) -> list[Selection]:
        """Retorna histórico de seleções"""
        return self.selection_history.copy()

    def clear_selection(self):
        """Limpa seleção ativa"""
        self.active_selection = None

    def clear_history(self):
        """Limpa histórico de seleções"""
        self.selection_history.clear()


# Funções de conveniência (backward compatibility)
def select_time_window(dataset: Dataset, start_seconds: float, end_seconds: float) -> Selection:
    """Seleção temporal (função de conveniência)"""
    selector = DataSelector()
    return selector.select_temporal(dataset, start_seconds, end_seconds)


def select_by_predicate(dataset: Dataset, series_id: str, predicate: Callable) -> Selection:
    """Seleção por predicado (função de conveniência)"""
    selector = DataSelector()
    return selector.select_by_predicate(dataset, predicate, series_id)
