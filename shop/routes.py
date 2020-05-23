from aiohttp import web

from shop import views


def setup_routes(app: web.Application) -> None:
    """
    Установка маршрутов для взаимодействия с приложением.

    :param app: экземпляр aiohttp-приложения
    """
    app.router.add_routes([
        web.post('/login', views.LoginView),
        web.view('/products', views.ProductListCreateView),
        web.view('/products/{slug}', views.ProductRetrieveUpdateDeleteView)
    ])
