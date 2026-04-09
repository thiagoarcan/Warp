import os
import sys
from pathlib import Path

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from PyQt6.QtWidgets import QApplication
from platform_base.core.dataset_store import DatasetStore
from platform_base.ui.state import SessionState
from platform_base.io.loader import load
from platform_base.ui.panels.data_panel import CompactDataPanel
from platform_base.ui.panels.viz_panel import ModernVizPanel


def main() -> int:
    app = QApplication.instance() or QApplication([])

    sample = Path(__file__).resolve().parents[1] / 'data' / 'samples' / 'BAR_DT-OP10.xlsx'
    if not sample.exists():
        raise FileNotFoundError(f'Amostra nao encontrada: {sample}')

    dataset = load(str(sample))
    store = DatasetStore()
    state = SessionState(store)
    dataset_id = state.add_dataset(dataset)
    state.set_current_dataset(dataset_id)

    panel_data = CompactDataPanel(state)
    panel_data._on_dataset_changed(dataset_id)

    rows = panel_data._data_table.rowCount() if hasattr(panel_data, '_data_table') else -1
    cols = panel_data._data_table.columnCount() if hasattr(panel_data, '_data_table') else -1

    if rows <= 0 or cols <= 0:
        raise RuntimeError(f'Data Panel nao renderizou tabela. rows={rows}, cols={cols}')

    panel_viz = ModernVizPanel(state)
    series_ids = list(dataset.series.keys())
    if not series_ids:
        raise RuntimeError('Dataset sem series para plot')

    panel_viz.create_plot_for_series(dataset_id, series_ids[0], '2d')
    plot_tabs = panel_viz._viz_tabs.count() if hasattr(panel_viz, '_viz_tabs') else -1

    if plot_tabs <= 1:
        raise RuntimeError(f'Viz Panel nao criou aba de plot. tabs={plot_tabs}')

    print(f'DATA_PANEL_ROWS={rows}')
    print(f'DATA_PANEL_COLS={cols}')
    print(f'VIZ_TABS={plot_tabs}')
    print('UAT_TEST_4=PASS')
    print('UAT_TEST_5=PASS')

    app.quit()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
