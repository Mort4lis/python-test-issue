from aiohttp import web

from shop import views


def setup_routes(app: web.Application) -> None:
    """
    Установка маршрутов для взаимодействия с приложением.

    :param app: экземпляр aiohttp-приложения
    """
    app.router.add_routes([
        web.post(r'/login', views.LoginView),
        web.view(r'/products', views.ProductListCreateView),
        web.view(r'/products/{slug}', views.ProductRetrieveUpdateDeleteView),
        web.view(r'/orders', views.OrderListCreateView),
        web.view(r'/orders/{number:\d+}', views.OrderRetrieveUpdateDeleteView)
    ])
