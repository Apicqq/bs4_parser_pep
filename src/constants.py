from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_MAIN_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active')
}


# оставил эти константы вне классов, чтобы проходили тесты.

class PathConstants:
    LOG_DIR = BASE_DIR / 'logs'
    DOWNLOADS_PATH = 'downloads'
    RESULTS_PATH = 'results'
    LOG_FILE = LOG_DIR / 'parser.log'


class UtilityConstants:
    PRETTY_OUTPUT_MODE = 'pretty'
    FILE_OUTPUT_MODE = 'file'
    DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
    LOGGER_DT_FORMAT = '%d.%m.%Y %H:%M:%S'
    LOGGER_FORMAT = (
        '%(levelname)s - %(asctime)s - %(lineno)s - %(funcName)s - '
        '%(message)s - %(name)s')


class Literals:
    ARCHIVE_DOWNLOADED = 'Архив был загружен и сохранён в: {}'
    UNEXPECTED_PEP_STATUS = ('Несовпадающие статусы:\n'
                             '{}\n'
                             'Статус в карточке: {}\n'
                             'Ожидаемые статусы: {}')
    PARSER_STARTED = 'Парсер был запущен'
    PARSER_ARGS = 'Аргументы командной строки: {}'
    PARSER_FINISHED = 'Работа парсера завершена'
    REQUEST_EXCEPTION = 'Возникла ошибка при загрузке страницы {}'
    PYTHON_VERSIONS_NOT_FOUND = 'Не найден список c версиями Python'
    TAG_NOT_FOUND = 'Не найден тег {} {}'
    COLLECTING_URLS = 'Собираем ссылки'
    COLLECTING_STATUSES = 'Собираем статусы'
