from shop.views import index, LoginView


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_post('/login', LoginView)
