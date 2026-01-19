from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from platform_base.viz.streaming import StreamingEngine


class AppState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    streaming_engines: dict[str, StreamingEngine] = Field(default_factory=dict)
    view_subscriptions: dict[str, str] = Field(default_factory=dict)
