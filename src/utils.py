import logging
from typing import Optional, Union

from bs4 import BeautifulSoup, Tag
from requests import RequestException
from requests_cache import CachedSession, Response

from constants import Literals
from exceptions import ParserFindTagException


def get_response(
        session: CachedSession, url: str, encoding: str = 'utf-8'
) -> Response:
    """
    Получить содержимое веб-страницы по указанному URL.

    :param session: CachedSession - сессия, используемая для запроса.
    :param url: URL веб-страницы.
    :param encoding: Кодировка веб-страницы, по умолчанию — utf-8.
    :returns: Объект ответа HTTP.
    :raises ConnectionError: Если произошла ошибка подключения.
    """
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(
            Literals.REQUEST_EXCEPTION.format(url, error)
        ) from error


def find_tag(soup: Union[BeautifulSoup, Tag], tag: str,
             attrs: Optional[dict] = None):
    """
    Находит указанный тег в объекте BeautifulSoup.

    :param soup: Объект BeautifulSoup или Tag, представляющий HTML-документ.
    :param tag: Имя тега, который нужно найти.
    :param attrs: Дополнительные атрибуты для поиска тега (необязательно).
    :return: Найденный тег.
    :raises ParserFindTagException: Если указанный тег не найден.
    """
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if not searched_tag:
        raise ParserFindTagException(Literals.TAG_NOT_FOUND.format(tag, attrs))
    return searched_tag


def get_soup(
        session: CachedSession,
        url: str,
        parser: str = 'lxml'
) -> BeautifulSoup:
    """
    Преобразует объект Response в BeautifulSoup.

    :param session: Объект Response, представляющий HTML-документ.
    :param url: URL веб-страницы.
    :param parser: Имя парсера, используемого
    для создания объекта BeautifulSoup.
    :return: Объект BeautifulSoup, представляющий HTML-документ.
    """
    return BeautifulSoup(get_response(session, url).text, parser)


def manage_logging(stack: list[Exception]) -> list:
    """
    Вспомогательная функция логгирования, которая выводит
    сообщения об ошибках в консоль.

    :param stack: Список ошибок, накопленных во время выполнения функции.

    :return: Список ошибок.
    """
    return list(map(lambda exception: logging.error(exception), stack))
