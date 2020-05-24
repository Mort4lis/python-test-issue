from aiohttp.web import View

from .services import ServiceFactory


class ServiceViewMixin(View):
    """Миксин, добавляющий объект фабрики для порождения объектов-сервисов."""

    def __init__(self, *args, **kwargs) -> None:
        """
        Инициализация view.

        Создает объект фабрики, для порождения сервисов.
        """
        super().__init__(*args, **kwargs)
        self.service_factory = ServiceFactory(conn=self.request['conn'])


class ProductServiceViewMixin(ServiceViewMixin):
    """Миксин, добавляющий сервис-объект для работы с продуктами."""

    def __init__(self, *args, **kwargs) -> None:
        """
        Инициализация view.

        Создает объект сервиса для работы с продуктами.
        """
        super().__init__(*args, **kwargs)
        self.product_service = self.service_factory.create_product_service()


class OrderServiceViewMixin(ServiceViewMixin):
    """Миксин, добавляющий сервис-объект для работы с заказами."""

    def __init__(self, *args, **kwargs) -> None:
        """
        Инициализация view.

        Создает объект сервиса для работы с заказами.
        """
        super().__init__(*args, **kwargs)
        self.order_service = self.service_factory.create_order_service()


class AuthServiceViewMixin(ServiceViewMixin):
    """Миксин, добавляющий сервис-объект для работы с аутентификацией."""

    def __init__(self, *args, **kwargs) -> None:
        """
        Инициализация view.

        Создает объект сервиса для работы с аутентификацией.
        """
        super().__init__(*args, **kwargs)
        self.auth_service = self.service_factory.create_auth_service()


class AccessTokenServiceViewMixin(ServiceViewMixin):
    """Миксин, добавляющий сервис-объект для работы с токенами."""

    def __init__(self, *args, **kwargs) -> None:
        """
        Инициализация view.

        Создает объект сервиса для работы с токенами.
        """
        super().__init__(*args, **kwargs)
        self.token_service = self.service_factory.create_access_token_service()
