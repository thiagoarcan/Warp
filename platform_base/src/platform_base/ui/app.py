from __future__ import annotations

import dash
import dash_bootstrap_components as dbc
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache

from platform_base.core.dataset_store import DatasetStore
from platform_base.ui.callbacks import register_callbacks
from platform_base.ui.layout import build_layout, LayoutConfig
from platform_base.ui.state import get_app_state
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


def create_app(store: DatasetStore | None = None, config: LayoutConfig | None = None) -> dash.Dash:
    """
    Cria aplicação Dash funcional conforme PRD seção 12.
    
    Features implementadas:
    - Layout responsivo configurável
    - Long callbacks para operações pesadas
    - Integração com AppState centralizado
    - Bootstrap para responsividade
    """
    # Setup app state
    app_state = get_app_state()
    if store:
        app_state.datasets = store
    
    # Setup long callback manager for async operations
    cache = diskcache.Cache("./.dash_cache")
    long_callback_manager = DiskcacheLongCallbackManager(cache)
    
    # Create Dash app with responsive theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.FONT_AWESOME,
            # Meta tag for mobile responsiveness
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
        suppress_callback_exceptions=True,
        long_callback_manager=long_callback_manager
    )
    
    # Configure layout
    layout_config = config or LayoutConfig()
    app.layout = build_layout(layout_config)
    
    # Register callbacks with app state
    register_callbacks(app, app_state)
    
    logger.info("dash_app_created", 
               responsive=layout_config.responsive,
               long_callbacks=True,
               theme="bootstrap")
    
    return app


def run_app(host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
    """
    Executa a aplicação Dash com configurações otimizadas.
    
    Args:
        host: Host para binding
        port: Porta para binding  
        debug: Modo debug (não recomendado para produção)
    """
    app = create_app()
    
    logger.info("starting_dash_server", 
               host=host, 
               port=port, 
               debug=debug)
    
    try:
        app.run_server(
            host=host,
            port=port,
            debug=debug,
            dev_tools_hot_reload=debug,
            dev_tools_silence_routes_logging=not debug
        )
    except Exception as e:
        logger.error("dash_server_failed", error=str(e))
        raise


def run():
    """Entry point for CLI command."""
    run_app()
