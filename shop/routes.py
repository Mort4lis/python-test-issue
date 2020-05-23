from shop import views
from aiohttp import web


def setup_routes(app):
    app.router.add_routes([
        web.get('/', views.index),
        web.post('/login', views.LoginView),
        web.view('/products', views.ProductListCreateView),
        web.view('/products/{slug}', views.ProductRetrieveUpdateDeleteView)
    ])
