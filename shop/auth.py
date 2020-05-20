from passlib.hash import sha256_crypt

from .dao import AccessTokenDAO, UserDAO
from .exceptions import DAOException


async def check_credentials(user_dao: UserDAO, login: str, password: str) -> bool:
    """
    Проверить аутентификационные данные пользователя.

    :param user_dao:
    :param login: логин пользователя
    :param password: пароль пользователя
    """
    try:
        user = await user_dao.get_by_login(login=login)
    except DAOException:
        return False
    return sha256_crypt.verify(password, user.password)


async def get_access_token(token_dao: AccessTokenDAO, login: str) -> str:
    """
    Вернуть токен пользователя.

    :param token_dao:
    :param login: логин пользователя
    """
    access_token = await token_dao.get_by_login(login=login)
    return access_token.token
