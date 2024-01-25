import logging
import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import MAIN_DOC_URL, BASE_DIR, PEP_MAIN_URL, EXPECTED_STATUS
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session: CachedSession) -> Optional[list[tuple[str, str, str]]]:
    """
    Парсит страницу "What's new" и возвращает список кортежей, содержащих
    ссылку на статью, заголовок, и информацию о редакторе и авторе.

    :param session: CachedSession - сессия, используемая для запроса.

    :returns: List[tuple[str, str, str]]: Список кортежей,
    содержащий ссылку на статью, заголовок, и её автора.
    """
    response = get_response(session, urljoin(MAIN_DOC_URL, 'whatsnew/'))
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    url_div = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = url_div.find_all('li',
                                          attrs={'class': 'toctree-l1'})
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python, 'Собираем ссылки', colour='red'):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(
            urljoin(MAIN_DOC_URL, 'whatsnew/'), version_a_tag['href']
        )
        response = get_response(session, version_link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        result.append((version_link, h1.text,
                       dl.text.replace('\n', ' ').strip()))
    return result


def latest_versions(session: CachedSession) -> Optional[
    list[tuple[str, str, str]]
]:
    """
    Получает ссылки на последние версии документации Python и возвращает
    список кортежей, содержащих ссылку на документацию, версию, и статус
    версии.

    :param session: CachedSession - сессия, используемая для запроса.

    :returns: Optional[list[tuple[str, str, str]]]: Список кортежей,
     содержащий ссылку на документацию, версию, и статус версии.

    """
    response = get_response(session, PEP_MAIN_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Не найден список c версиями Python')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in tqdm(a_tags, 'Собираем ссылки', colour='red'):
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session: CachedSession) -> None:
    """
    Скачивает архив документации Python и сохраняет его в каталог "downloads".

    Args:
    :param session: CachedSession - сессия, используемая для запроса.

    :returns: None
    """
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(soup, 'div', attrs={'class': 'body', 'role': 'main'})
    table = find_tag(main_div, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(r'.+?pdf-a4\.zip')})
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session: CachedSession) -> Optional[list[tuple[str, str]]]:
    """
    Собирает статусы PEP из основного каталога PEP и возвращает
    список кортежей, содержащий статус и количество PEP с этим статусом.

    :param session: CachedSession - сессия, используемая для запроса.

    :returns: List[tuple[str, str]]: Список кортежей,
     содержащих статус и количество PEP с этим статусом.

    """
    response = get_response(session, PEP_MAIN_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    pep_relative_links = sorted(set(
        [url.get('href') for url in soup.select(
            'section#numerical-index .pep-zero-table.docutils.align-default a'
        )]))
    table_statuses = [
        abbr.text[1:] for abbr in find_tag(
            soup, 'section', attrs={'id': 'numerical-index'}
        ).find(
            class_='pep-zero-table docutils align-default'
        ).find_all(
            'abbr', string=re.compile(r'^\w*$')
        )
    ]
    pep_status_codes = {}
    results = [('Статус', 'Количество')]
    for number, url in tqdm(enumerate(pep_relative_links),
                            'Собираем статусы', colour='red'):
        response = get_response(session, urljoin(PEP_MAIN_URL, url))
        soup = BeautifulSoup(response.text, 'lxml')
        page_status = soup.find(
            class_='rfc2822 field-list simple'
        ).find('abbr').text
        if (page_status and page_status not in
                EXPECTED_STATUS.get(table_statuses[number])):
            logging.warning(
                'Несовпадающие статусы:\n'
                f'{urljoin(PEP_MAIN_URL, url)}\n'
                f'Статус в карточке: {page_status}\n'
                f'Ожидаемые статусы:'
                f' {EXPECTED_STATUS.get(table_statuses[number])}'
            )
        if page_status not in pep_status_codes:
            pep_status_codes[page_status] = 1
        else:
            pep_status_codes[page_status] += 1
    results.extend(list(pep_status_codes.items()))
    results.append(('Total', str(sum(pep_status_codes.values()))))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
    """
    Основная функция для запуска парсера.

    Эта функция конфигурирует логгер, парсит аргументы командной строки,
    инициализирует сессию, очищает кэш, если указано, запускает
    парсер на основе режима, указанного в аргументах командной строки,
    и контролирует вывод результата.

    :returns: None
    """

    configure_logging()
    logging.info('Парсер запущен')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results:
        control_output(results, args)
    logging.info('Парсер завершил работу')


if __name__ == '__main__':
    main()
