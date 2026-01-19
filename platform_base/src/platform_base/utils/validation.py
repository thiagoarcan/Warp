from typing import Type

from pydantic import BaseModel, ValidationError as PydanticValidationError

from platform_base.utils.errors import ValidationError
from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


def validate_config(config_dict: dict, schema: Type[BaseModel]) -> BaseModel:
    """Validate config dict against a Pydantic schema."""
    try:
        return schema(**config_dict)
    except PydanticValidationError as exc:
        logger.error("config_validation_failed", errors=exc.errors())
        raise ValidationError("Config validation failed", {"errors": exc.errors()}) from exc
