from passlib.hash import sha256_crypt

from .dao import SqlAlchemyTokenDAO, SqlAlchemyUserDAO


async def check_credentials(db_engine, login: str, password: str) -> bool:
    """
    Проверить аутентификационные данные пользователя.

    :param db_engine:
    :param login: логин пользователя
    :param password: пароль пользователя
    """
    async with db_engine.acquire() as conn:
        user_dao = SqlAlchemyUserDAO(conn)
        user = await user_dao.get_by_login(login=login)

        if user is not None:
            return sha256_crypt.verify(password, user.password)
        return False


async def get_access_token(db_engine, login: str) -> str:
    """
    Вернуть токен пользователя.

    :param db_engine:
    :param login: логин пользователя
    """
    async with db_engine.acquire() as conn:
        token_dao = SqlAlchemyTokenDAO(conn)
        access_token = await token_dao.get_by_login(login=login)
        return access_token.token
