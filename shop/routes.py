from shop.views import index, LoginView, ProductListCreateView


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_post('/login', LoginView)
    app.router.add_get('/products', ProductListCreateView)
    app.router.add_post('/products', ProductListCreateView)
