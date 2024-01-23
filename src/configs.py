import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR, LOGGER_DT_FORMAT

LOGGER_FORMAT = ('%(levelname)s - %(asctime)s - %(lineno)s - %(funcName)s - '
                 '%(message)s - %(name)s')


def configure_parser(modes):
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
        help='Очистить кэш'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Формат вывода'
    )
    return parser


def configure_logger():
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotating_handler = RotatingFileHandler(
        log_file,
        maxBytes=1_000_000,
        backupCount=5,
        encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=LOGGER_DT_FORMAT,
        format=LOGGER_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
