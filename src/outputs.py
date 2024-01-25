import csv
import datetime as dt
from argparse import Namespace

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results: list, cli_args: Namespace) -> None:
    """
    Управляет выводом в зависимости от аргументов командной строки.

    :param results: Результаты, которые нужно вывести.
    :param cli_args: Аргументы командной строки, включая аргумент для вывода.
    """
    output = cli_args.output
    # Изначально сделал, используя match case, но сервера яндекса не
    # поддерживают питон выше 3.9
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results: list) -> None:
    """
    Выводит результаты по умолчанию.

    :param results: Результаты, которые нужно вывести.
    """
    for result in results:
        print(*result)


def pretty_output(results: list) -> None:
    """
    Выводит отформатированную таблицу PrettyTable на основе результатов.

    :param results: Результаты, которые нужно вывести.
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
    """
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    current_time = dt.datetime.now().strftime(DATETIME_FORMAT)
    filename = f'{parser_mode}_{current_time}.csv'
    filepath = results_dir / filename
    with open(filepath, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(results)
