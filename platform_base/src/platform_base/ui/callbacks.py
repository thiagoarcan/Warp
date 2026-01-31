from __future__ import annotations

import base64
import tempfile
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate

from platform_base.core.models import TimeWindow, ViewData
from platform_base.io.loader import load
from platform_base.processing.calculus import derivative, integral
from platform_base.processing.interpolation import interpolate
from platform_base.processing.synchronization import synchronize
from platform_base.ui.export import export_selection, export_session
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


def _create_empty_figure(message: str = "No data to display") -> go.Figure:
    """Create an empty figure with a message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font={"size": 16, "color": "gray"},
    )
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        plot_bgcolor="white",
    )
    return fig


def _create_timeseries_figure(
    t_seconds: np.ndarray,
    series_dict: dict[str, np.ndarray],
    title: str = "Time Series",
    show_interpolated: bool = True,
    interp_mask: dict[str, np.ndarray] | None = None,
) -> go.Figure:
    """Create a timeseries plot figure"""
    fig = go.Figure()

    colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    ]

    for i, (name, values) in enumerate(series_dict.items()):
        color = colors[i % len(colors)]

        # Main trace
        fig.add_trace(go.Scatter(
            x=t_seconds,
            y=values,
            mode="lines",
            name=name,
            line={"color": color, "width": 1.5},
            hovertemplate=f"{name}<br>t=%{{x:.2f}}s<br>value=%{{y:.4f}}<extra></extra>",
        ))

        # Mark interpolated points if mask provided
        if interp_mask and name in interp_mask and show_interpolated:
            mask = interp_mask[name]
            if np.any(mask):
                fig.add_trace(go.Scatter(
                    x=t_seconds[mask],
                    y=values[mask],
                    mode="markers",
                    name=f"{name} (interpolated)",
                    marker={
                        "color": color,
                        "size": 4,
                        "symbol": "circle-open",
                        "line": {"width": 1},
                    },
                    hovertemplate=f"{name} (interp)<br>t=%{{x:.2f}}s<br>value=%{{y:.4f}}<extra></extra>",
                ))

    fig.update_layout(
        title=title,
        xaxis_title="Time (seconds)",
        yaxis_title="Value",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        hovermode="x unified",
        template="plotly_white",
    )

    return fig


def register_callbacks(app, app_state):
    """Register all Dash callbacks for the application"""

    # ========================================================================
    # Data Upload and Selection Callbacks
    # ========================================================================

    @app.callback(
        Output("dataset-dropdown", "options"),
        Output("dataset-store", "data"),
        Output("notifications", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def _on_upload(contents, filename):
        """Handle file upload"""
        if contents is None:
            return [], None, None

        try:
            _, content_string = contents.split(",", 1)
            decoded = base64.b64decode(content_string)
            suffix = Path(filename).suffix

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(decoded)
                tmp_path = tmp.name

            dataset = load(tmp_path, config={"max_rows": 100000})
            dataset_id = app_state.datasets.add_dataset(dataset)

            logger.info("upload_loaded", dataset_id=dataset_id, filename=filename)

            # Get all datasets for dropdown
            all_ids = [ds.dataset_id for ds in app_state.datasets.list_datasets()]
            options = [{"label": ds_id, "value": ds_id} for ds_id in all_ids]

            # Success notification (would be a toast in real implementation)
            notification = None

            return options, dataset_id, notification

        except Exception as e:
            logger.exception("upload_failed", filename=filename, error=str(e))
            return no_update, no_update, f"Upload failed: {e!s}"

    @app.callback(
        Output("series-dropdown", "options"),
        Output("time-range-slider", "min"),
        Output("time-range-slider", "max"),
        Output("time-range-slider", "value"),
        Output("time-range-slider", "marks"),
        Input("dataset-store", "data"),
        prevent_initial_call=True,
    )
    def _update_series_and_time(dataset_id):
        """Update series dropdown and time range when dataset changes"""
        if not dataset_id:
            return [], 0, 100, [0, 100], {}

        try:
            dataset = app_state.datasets.get_dataset(dataset_id)
            series_options = [
                {"label": name, "value": name}
                for name in dataset.series
            ]

            t_min = float(np.nanmin(dataset.t_seconds))
            t_max = float(np.nanmax(dataset.t_seconds))

            # Create marks for slider
            n_marks = 5
            mark_values = np.linspace(t_min, t_max, n_marks)
            marks = {int(v): f"{v:.1f}s" for v in mark_values}

            return series_options, t_min, t_max, [t_min, t_max], marks

        except Exception as e:
            logger.exception("update_series_failed", error=str(e))
            return [], 0, 100, [0, 100], {}

    # ========================================================================
    # Visualization Callbacks
    # ========================================================================

    @app.callback(
        Output("main-plot", "figure"),
        Input("series-dropdown", "value"),
        Input("time-range-slider", "value"),
        Input("interp-method", "value"),
        Input("calc-operation", "value"),
        Input("calc-method", "value"),
        Input("sync-method", "value"),
        State("dataset-store", "data"),
        prevent_initial_call=True,
    )
    def _update_plot(
        selected_series,
        time_range,
        interp_method,
        calc_operation,
        calc_method,
        sync_method,
        dataset_id,
    ):
        """Update main plot based on selections and processing options"""
        if not dataset_id or not selected_series:
            return _create_empty_figure("Select a dataset and series to visualize")

        try:
            dataset = app_state.datasets.get_dataset(dataset_id)

            # Filter by time range
            t_seconds = dataset.t_seconds
            mask = (t_seconds >= time_range[0]) & (t_seconds <= time_range[1])
            t_filtered = t_seconds[mask]

            if len(t_filtered) == 0:
                return _create_empty_figure("No data in selected time range")

            # Collect series data
            series_data = {}
            interp_masks = {}

            for series_name in selected_series:
                if series_name not in dataset.series:
                    continue

                series = dataset.series[series_name]
                values = series.values[mask].copy()

                # Apply interpolation if requested
                if interp_method and interp_method != "none":
                    try:
                        result = interpolate(values, t_filtered, interp_method, {})
                        values = result.values
                        interp_masks[series_name] = result.interpolation_info.is_interpolated_mask
                    except Exception as e:
                        logger.warning("interpolation_failed",
                                      method=interp_method, error=str(e))

                series_data[series_name] = values

            # Apply synchronization if requested
            if sync_method and sync_method != "none" and len(series_data) > 1:
                try:
                    t_dict = dict.fromkeys(series_data, t_filtered)
                    result = synchronize(series_data, t_dict, sync_method, {})
                    series_data = result.synced_series
                    t_filtered = result.t_common
                except Exception as e:
                    logger.warning("sync_failed", method=sync_method, error=str(e))

            # Apply calculus operations if requested
            if calc_operation and calc_operation != "none":
                processed_data = {}
                for name, values in series_data.items():
                    try:
                        if calc_operation.startswith("derivative_"):
                            order = int(calc_operation.split("_")[1])
                            result = derivative(values, t_filtered, order, calc_method, {})
                            processed_data[f"{name}_d{order}"] = result.values
                        elif calc_operation == "integral":
                            result = integral(values, t_filtered, "trapezoid", {})
                            processed_data[f"{name}_int"] = result.values
                    except Exception as e:
                        logger.warning("calculus_failed",
                                      operation=calc_operation, error=str(e))
                        processed_data[name] = values

                if processed_data:
                    series_data = processed_data

            # Create figure
            return _create_timeseries_figure(
                t_filtered,
                series_data,
                title=f"Dataset: {dataset_id}",
                interp_mask=interp_masks,
            )


        except Exception as e:
            logger.exception("plot_update_failed", error=str(e))
            return _create_empty_figure(f"Error: {e!s}")

    # ========================================================================
    # Streaming Controls Callbacks
    # ========================================================================

    @app.callback(
        Output("streaming-controls", "is_open"),
        Input("btn-stream", "n_clicks"),
        State("streaming-controls", "is_open"),
        prevent_initial_call=True,
    )
    def _toggle_streaming_controls(n_clicks, is_open):
        """Toggle streaming controls panel visibility"""
        return not is_open

    @app.callback(
        Output("streaming-state", "data"),
        Output("streaming-interval", "disabled"),
        Input("btn-play", "n_clicks"),
        Input("btn-pause", "n_clicks"),
        Input("btn-stop", "n_clicks"),
        Input("btn-first", "n_clicks"),
        Input("btn-last", "n_clicks"),
        Input("btn-forward", "n_clicks"),
        Input("btn-backward", "n_clicks"),
        State("streaming-state", "data"),
        State("dataset-store", "data"),
        State("speed-slider", "value"),
        State("window-size", "value"),
        State("streaming-options", "value"),
        prevent_initial_call=True,
    )
    def _handle_streaming_controls(
        play_clicks, pause_clicks, stop_clicks,
        first_clicks, last_clicks, forward_clicks, backward_clicks,
        current_state, dataset_id, speed, window_size, options,
    ):
        """Handle streaming playback controls"""
        if not dataset_id:
            raise PreventUpdate

        triggered_id = ctx.triggered_id

        # Initialize state if needed
        if not current_state:
            current_state = {
                "session_id": f"stream_{dataset_id}",
                "is_playing": False,
                "current_index": 0,
                "speed": speed or 1.0,
                "window_size": window_size or 60,
                "loop": "loop" in (options or []),
            }

        # Get dataset for bounds
        try:
            dataset = app_state.datasets.get_dataset(dataset_id)
            max_index = len(dataset.t_seconds) - 1
        except Exception:
            max_index = 1000

        # Handle button actions
        if triggered_id == "btn-play":
            current_state["is_playing"] = True
            logger.info("streaming_play_requested")

        elif triggered_id == "btn-pause":
            current_state["is_playing"] = False
            logger.info("streaming_pause_requested")

        elif triggered_id == "btn-stop":
            current_state["is_playing"] = False
            current_state["current_index"] = 0
            logger.info("streaming_stop_requested")

        elif triggered_id == "btn-first":
            current_state["current_index"] = 0

        elif triggered_id == "btn-last":
            current_state["current_index"] = max_index

        elif triggered_id == "btn-forward":
            current_state["current_index"] = min(
                current_state["current_index"] + int(speed * 10),
                max_index,
            )

        elif triggered_id == "btn-backward":
            current_state["current_index"] = max(
                current_state["current_index"] - int(speed * 10),
                0,
            )

        # Update speed and options
        current_state["speed"] = speed or 1.0
        current_state["window_size"] = window_size or 60
        current_state["loop"] = "loop" in (options or [])

        # Interval disabled when not playing
        interval_disabled = not current_state["is_playing"]

        return current_state, interval_disabled

    @app.callback(
        Output("streaming-state", "data", allow_duplicate=True),
        Input("streaming-interval", "n_intervals"),
        State("streaming-state", "data"),
        State("dataset-store", "data"),
        prevent_initial_call=True,
    )
    def _streaming_tick(n_intervals, state, dataset_id):
        """Handle streaming interval tick"""
        if not state or not state.get("is_playing") or not dataset_id:
            raise PreventUpdate

        try:
            dataset = app_state.datasets.get_dataset(dataset_id)
            max_index = len(dataset.t_seconds) - 1

            # Advance index
            new_index = state["current_index"] + int(state["speed"])

            if new_index >= max_index:
                if state.get("loop"):
                    new_index = 0
                else:
                    new_index = max_index
                    state["is_playing"] = False

            state["current_index"] = new_index

            return state

        except Exception as e:
            logger.exception("streaming_tick_failed", error=str(e))
            raise PreventUpdate

    # ========================================================================
    # Export Callbacks
    # ========================================================================

    @app.callback(
        Output("notifications", "children", allow_duplicate=True),
        Input("btn-export-csv", "n_clicks"),
        Input("btn-export-xlsx", "n_clicks"),
        Input("btn-export-parquet", "n_clicks"),
        State("dataset-store", "data"),
        State("series-dropdown", "value"),
        State("time-range-slider", "value"),
        prevent_initial_call=True,
    )
    def _handle_export_data(csv_clicks, xlsx_clicks, parquet_clicks,
                           dataset_id, selected_series, time_range):
        """Handle data export buttons"""
        if not dataset_id or not selected_series:
            return "Please select a dataset and series first"

        triggered_id = ctx.triggered_id

        format_map = {
            "btn-export-csv": "csv",
            "btn-export-xlsx": "xlsx",
            "btn-export-parquet": "parquet",
        }

        export_format = format_map.get(triggered_id, "csv")

        try:
            dataset = app_state.datasets.get_dataset(dataset_id)

            # Filter by time range
            t_seconds = dataset.t_seconds
            mask = (t_seconds >= time_range[0]) & (t_seconds <= time_range[1])
            t_filtered = t_seconds[mask]

            # Build series dict
            series_dict = {}
            for name in selected_series:
                if name in dataset.series:
                    series_dict[name] = dataset.series[name].values[mask]

            # Create ViewData
            view_data = ViewData(
                dataset_id=dataset_id,
                series=series_dict,
                t_seconds=t_filtered,
                t_datetime=dataset.t_datetime[mask],
                window=TimeWindow(start_seconds=time_range[0], end_seconds=time_range[1]),
            )

            # Export
            output_path = Path(f"export_{dataset_id}.{export_format}")
            result = export_selection(view_data, export_format, output_path)

            return f"Exported to {result.path} ({result.rows_exported} rows, {result.size_bytes/1024:.1f} KB)"

        except Exception as e:
            logger.exception("export_failed", format=export_format, error=str(e))
            return f"Export failed: {e!s}"

    @app.callback(
        Output("notifications", "children", allow_duplicate=True),
        Input("btn-export-session", "n_clicks"),
        prevent_initial_call=True,
    )
    def _handle_export_session(n_clicks):
        """Handle session export button"""
        if not n_clicks:
            raise PreventUpdate

        try:
            output_path = Path(f"session_{int(__import__('time').time())}.json")
            result = export_session(output_path, app_state)

            return f"Session exported to {result.path} ({result.size_bytes} bytes)"

        except Exception as e:
            logger.exception("session_export_failed", error=str(e))
            return f"Session export failed: {e!s}"

    # ========================================================================
    # Results Panel Callbacks
    # ========================================================================

    @app.callback(
        Output("results-collapse", "is_open"),
        Input("btn-close-results", "n_clicks"),
        State("results-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def _toggle_results_panel(n_clicks, is_open):
        """Toggle results panel visibility"""
        return not is_open

    @app.callback(
        Output("results-content", "children"),
        Input("results-tabs", "active_tab"),
        State("dataset-store", "data"),
        State("series-dropdown", "value"),
        State("time-range-slider", "value"),
        prevent_initial_call=True,
    )
    def _update_results_content(active_tab, dataset_id, selected_series, time_range):
        """Update results panel content based on active tab"""
        from dash import html

        if active_tab == "stats" and dataset_id and selected_series:
            try:
                dataset = app_state.datasets.get_dataset(dataset_id)

                stats_rows = []
                for name in selected_series:
                    if name not in dataset.series:
                        continue

                    values = dataset.series[name].values
                    t_seconds = dataset.t_seconds

                    # Apply time filter
                    mask = (t_seconds >= time_range[0]) & (t_seconds <= time_range[1])
                    values = values[mask]

                    stats_rows.append(html.Tr([
                        html.Td(name),
                        html.Td(f"{np.nanmin(values):.4f}"),
                        html.Td(f"{np.nanmax(values):.4f}"),
                        html.Td(f"{np.nanmean(values):.4f}"),
                        html.Td(f"{np.nanstd(values):.4f}"),
                        html.Td(str(len(values))),
                    ]))

                return html.Table([
                    html.Thead(html.Tr([
                        html.Th("Series"),
                        html.Th("Min"),
                        html.Th("Max"),
                        html.Th("Mean"),
                        html.Th("Std"),
                        html.Th("Count"),
                    ])),
                    html.Tbody(stats_rows),
                ], className="table table-striped")

            except Exception as e:
                return html.P(f"Error computing statistics: {e!s}")

        elif active_tab == "logs":
            return html.Pre("Logs would be displayed here...",
                          style={"maxHeight": "200px", "overflow": "auto"})

        elif active_tab == "perf":
            return html.Div([
                html.P("Performance metrics:"),
                html.Ul([
                    html.Li("Plot render time: N/A"),
                    html.Li("Data processing time: N/A"),
                    html.Li("Memory usage: N/A"),
                ]),
            ])

        return html.P("Select a tab to view content")

    logger.info("callbacks_registered", n_callbacks=10)
