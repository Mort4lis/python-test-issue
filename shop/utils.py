import json
from decimal import Decimal
from typing import Any
from uuid import UUID


class UUIDEncoderMixin(json.JSONEncoder):
    """Миксин, реализующий поведение сериализации объектов класса `UUID`."""

    def default(self, obj: Any) -> Any:
        """
        Сериализация объекта класса `UUID`.

        :param obj: сериализуемый объект
        :return: сереализуемое представление объекта
        """
        if isinstance(obj, UUID):
            return obj.hex
        return super().default(obj)


class DecimalEncoderMixin(json.JSONEncoder):
    """Миксин, реализующий поведение сериализации объектов класса `Decimal`."""

    def default(self, obj: Any) -> Any:
        """
        Сериализация объекта класса `Decimal`.

        :param obj: сериализуемый объект
        :return: сереализуемое представление объекта
        """
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class JsonEncoder(UUIDEncoderMixin, DecimalEncoderMixin, json.JSONEncoder):
    """Json-сериализатор, используемый для сериализации сущностей бизнес-логики."""

    pass
