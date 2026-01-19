# Platform Base v2.0

Platform Base is an exploratory time-series toolkit for irregular sensor data.

## Quickstart

```bash
pip install -e .
```

```python
from platform_base import load_dataset
from platform_base.processing.interpolation import interpolate

# Load a dataset
result = load_dataset("path/to/sensor_data.xlsx")

# Interpolate a series
series_id = next(iter(result.series))
interp = interpolate(
    result.series[series_id].values,
    result.t_seconds,
    method="linear",
    params={},
)
```

## Development

```bash
pytest tests/
```
