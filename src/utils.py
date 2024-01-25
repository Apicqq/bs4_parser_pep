# Название этого файла — антипаттерн. Логичнее его было бы назвать, например,
# services или helpers.

import logging
from typing import Optional

from bs4 import BeautifulSoup
from requests import RequestException
from requests_cache import CachedSession

from exceptions import ParserFindTagException


def get_response(session: CachedSession, url: str):
    """
    Получить содержимое веб-страницы по указанному URL.

    :param session: CachedSession - сессия, используемая для запроса.
    :param url: URL веб-страницы.
    :returns: Объект ответа HTTP.
    """
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(f'Возникла ошибка при загрузке страницы {url}',
                          stack_info=True)


def find_tag(soup: BeautifulSoup, tag: str, attrs: Optional[dict] = None):
    """
    Находит указанный тег в объекте BeautifulSoup.

    :param soup: Объект BeautifulSoup, представляющий HTML-документ.
    :param tag: Имя тега, который нужно найти.
    :param attrs: Дополнительные атрибуты для поиска тега (необязательно).
    :return: Найденный тег.
    :raises ParserFindTagException: Если указанный тег не найден.
    """
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if not searched_tag:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
