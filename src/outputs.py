import csv
import datetime as dt
from argparse import Namespace

from prettytable import PrettyTable

from constants import BASE_DIR, PathConstants, UtilityConstants


def default_output(results: list, *args) -> None:
    """
    Выводит результаты по умолчанию.

    :param results: Результаты, которые нужно вывести.

    :returns: None
    """
    for result in results:
        print(*result)


def pretty_output(results: list, *args) -> None:
    """
    Выводит отформатированную таблицу PrettyTable на основе результатов.

    :param results: Результаты, которые нужно вывести.

    :returns: None
    """
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(
        results: list,
        cli_args: Namespace,
        encoding: str = 'utf-8'
) -> None:
    """
    Выводит результаты в файл CSV на основе результатов
    и аргументов командной строки.

    :param results: Результаты, которые нужно вывести.
    :param cli_args: Аргументы командной строки, включая режим парсера.
    :param encoding: Кодировка файла.

    :returns: None
    """
    results_dir = BASE_DIR / PathConstants.RESULTS_PATH
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    current_time = dt.datetime.now().strftime(UtilityConstants.DATETIME_FORMAT)
    filename = f'{parser_mode}_{current_time}.csv'
    filepath = results_dir / filename
    with open(filepath, 'w', encoding=encoding) as file:
        csv.writer(file, dialect=csv.excel).writerows(results)


OUTPUT_MODES = {
    UtilityConstants.PRETTY_OUTPUT_MODE: pretty_output,
    UtilityConstants.FILE_OUTPUT_MODE: file_output,
    UtilityConstants.DEFAULT_OUTPUT_MODE: default_output
}


def control_output(results: list, cli_args: Namespace) -> None:
    """
    Управляет выводом в зависимости от аргументов командной строки.

    :param results: Результаты, которые нужно вывести.
    :param cli_args: Аргументы командной строки, включая аргумент для вывода.

    :returns: None
    """
    output = cli_args.output
    selected_output = OUTPUT_MODES.get(
        output, OUTPUT_MODES.get(UtilityConstants.DEFAULT_OUTPUT_MODE)
    )
    selected_output(results, cli_args)
