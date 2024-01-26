import csv
import datetime as dt
from argparse import Namespace

from prettytable import PrettyTable

from constants import BASE_DIR, PathConstants, UtilityConstants


def control_output(results: list, cli_args: Namespace) -> None:
    """
    Управляет выводом в зависимости от аргументов командной строки.

    :param results: Результаты, которые нужно вывести.
    :param cli_args: Аргументы командной строки, включая аргумент для вывода.

    :returns: None
    """
    output = cli_args.output
    output_methods = {
        'pretty': pretty_output,
        'file': file_output,
        'default': default_output
    }
    selected_output = output_methods.get(output, default_output)
    selected_output(results, cli_args)


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


def file_output(results: list, cli_args: Namespace) -> None:
    """
    Выводит результаты в файл CSV на основе результатов
    и аргументов командной строки.

    :param results: Результаты, которые нужно вывести.
    :param cli_args: Аргументы командной строки, включая режим парсера.

    :returns: None
    """
    results_dir = BASE_DIR / PathConstants.RESULTS_PATH
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    current_time = dt.datetime.now().strftime(UtilityConstants.DATETIME_FORMAT)
    filename = f'{parser_mode}_{current_time}.csv'
    filepath = results_dir / filename
    with open(filepath, 'w', encoding='utf-8') as file:
        csv.writer(file, dialect='excel').writerows(results)
