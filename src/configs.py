import argparse
import logging
from logging.handlers import RotatingFileHandler

from requests_cache import CachedSession

from constants import PathConstants, UtilityConstants


def configure_argument_parser(
        modes: dict[str, CachedSession].keys
) -> argparse.ArgumentParser:
    """
    Настраивает ArgumentParser для командной строки.

    :param modes : dict[str, CachedSession].keys - Список режимов работы.

    :returns: ArgumentParser: - Сконфигурированный парсер аргументов
    командной строки.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'mode',
        choices=modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=
        (UtilityConstants.PRETTY_OUTPUT_MODE,
         UtilityConstants.FILE_OUTPUT_MODE),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging() -> None:
    """
    Настраивает логирование для приложения.

    Создает каталог для логов, если его не существует,
    и настраивает RotatingHandler для записи логов в файл.

    :returns: None
    """
    log_dir = PathConstants.LOG_DIR
    log_dir.mkdir(exist_ok=True)
    log_file = PathConstants.LOG_FILE
    rotating_handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,
        backupCount=5,
        encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=UtilityConstants.LOGGER_DT_FORMAT,
        format=UtilityConstants.LOGGER_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
