# https://github.com/pydantic/pydantic/issues/1223
# https://github.com/pydantic/pydantic/pull/3179
# https://github.com/pydantic/pydantic/issues/1673

from collections.abc import Callable
from copy import deepcopy
from typing import Any, TypeVar

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

Model = TypeVar("Model", bound=type[BaseModel])


def optional(without_fields: list[str] | None = None) -> Callable[[Model], Model]:
    """A decorator that create a partial model.

    Args:
        model (Type[BaseModel]): BaseModel model.

    Returns:
        Type[BaseModel]: ModelBase partial model.
    """
    if without_fields is None:
        without_fields = []

    def wrapper(model: type[Model]) -> type[Model]:
        base_model: type[Model] = model

        def make_field_optional(
            field: FieldInfo, default: Any = None
        ) -> tuple[Any, FieldInfo]:
            new = deepcopy(field)
            new.default = default
            new.annotation = field.annotation | None
            return new.annotation, new

        if without_fields:
            base_model = BaseModel

        return create_model(
            model.__name__,
            __base__=base_model,
            __module__=model.__module__,
            **{
                field_name: make_field_optional(field_info)
                for field_name, field_info in model.model_fields.items()
                if field_name not in without_fields
            },
        )

    return wrapper
