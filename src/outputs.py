import csv
import datetime as dt

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    output = cli_args.output
    match output:
        case 'pretty':
            pretty_output(results)
        case 'file':
            file_output(results, cli_args)
        case _:
            default_output(results)


def default_output(results):
    for result in results:
        print(*result)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    current_time = dt.datetime.now().strftime(DATETIME_FORMAT)
    filename = f'{parser_mode}_{current_time}.csv'
    filepath = results_dir / filename
    with open(filepath, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(results)
