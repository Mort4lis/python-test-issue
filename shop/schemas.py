AUTH_SCHEMA = {
    'type': 'object',
    'properties': {
        'login': {'type': 'string'},
        'password': {'type': 'string'}
    },
    'required': ['login', 'password'],
    'additionalProperties': False
}

PRODUCT_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string', 'minLength': 1, 'maxLength': 255},
        'description': {'type': 'string', 'minLength': 5},
        'price': {'type': 'number', 'minimum': 0.1},
        'left_in_stock': {'type': 'integer', 'minimum': 1}
    },
    'required': ['name', 'description', 'price', 'left_in_stock'],
    'additionalProperties': False
}

ORDER_PRODUCT_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'product': {'type': 'string'},
            'quantity': {'type': 'integer', 'minimum': 1}
        },
        'required': ['product', 'quantity'],
        'additionalProperties': False
    },
    'minItems': 1
}
