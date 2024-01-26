import logging
import re
from collections import defaultdict
from typing import Optional
from urllib.parse import urljoin

from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    Literals, PathConstants, BASE_DIR,
    MAIN_DOC_URL, PEP_MAIN_URL, EXPECTED_STATUS, UtilityConstants
)
from outputs import control_output
from utils import find_tag, get_response, get_soup


def whats_new(session: CachedSession) -> Optional[list[tuple[str, str, str]]]:
    """
    Парсит страницу "What's new" и возвращает список кортежей, содержащих
    ссылку на статью, заголовок, и информацию о редакторе и авторе.

    :param session: CachedSession - сессия, используемая для запроса.

    :returns: List[tuple[str, str, str]]: Список кортежей,
    содержащий ссылку на статью, заголовок, и её автора.
    """
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for tag in tqdm(
        get_soup(session, urljoin(MAIN_DOC_URL, 'whatsnew/')).select(
                '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > a'
        ), Literals.COLLECTING_URLS, colour=UtilityConstants.PROGRESS_BAR_COLOR
    ):
        version_link = urljoin(
            urljoin(MAIN_DOC_URL, 'whatsnew/'),
            tag.get('href')
        )
        if not version_link:
            continue
        soup = get_soup(session, version_link)
        result.append((version_link, find_tag(soup, 'h1').text,
                       find_tag(soup, 'dl').text.replace(
                           '\n', ' '
                       ).strip()))
        continue
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
    soup = get_soup(session, MAIN_DOC_URL)
    ul_tags = soup.select('div.sphinxsidebarwrapper > ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise RuntimeError(Literals.PYTHON_VERSIONS_NOT_FOUND)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in tqdm(
            a_tags,
            Literals.COLLECTING_URLS,
            colour=UtilityConstants.PROGRESS_BAR_COLOR
    ):
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session: CachedSession) -> None:
    """
    Скачивает архив документации Python и сохраняет его в каталог "downloads".

    :param session: CachedSession - сессия, используемая для запроса.

    :returns: None
    """
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    pdf_relative_url = get_soup(session, downloads_url).select_one(
        'div.body > table.docutils a[href$="pdf-a4.zip"]'
    )['href']
    archive_url = urljoin(downloads_url, pdf_relative_url)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / PathConstants.DOWNLOADS_PATH
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = get_response(session, archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(Literals.ARCHIVE_DOWNLOADED.format(archive_path))


def pep(session: CachedSession) -> Optional[list[tuple[str, str]]]:
    """
    Собирает статусы PEP из основного каталога PEP и возвращает
    список кортежей, содержащий статус и количество PEP с этим статусом.

    :param session: CachedSession - сессия, используемая для запроса.

    :returns: List[tuple[str, str]]: Список кортежей,
     содержащих статус и количество PEP с этим статусом.

    """
    soup = get_soup(session, PEP_MAIN_URL)
    pep_relative_links = sorted(set(
        [url.get('href') for url in soup.select(
            'section#numerical-index .pep-zero-table.docutils.align-default a'
        )]
    ))
    table_statuses = [
        abbr.text[1:] for abbr in soup.select(
            'section#numerical-index .pep-zero-table.'
            'docutils.align-default abbr'
        )
    ]
    pep_status_codes = defaultdict(int)
    mismatches = []
    for number, url in tqdm(
        enumerate(pep_relative_links),
        Literals.COLLECTING_STATUSES,
        colour=UtilityConstants.PROGRESS_BAR_COLOR,
        total=len(pep_relative_links)
    ):
        if not url:
            continue
        soup = get_soup(session, urljoin(PEP_MAIN_URL, url))
        page_status = soup.select_one('#pep-content > dl abbr').text
        if (page_status and page_status not in
                EXPECTED_STATUS.get(table_statuses[number])):
            mismatches.append(
                (url, page_status, table_statuses[number], number)
            )
        pep_status_codes[page_status] += 1
    if mismatches:
        for url, page_status, table_status, number in mismatches:
            logging.warning(
                Literals.UNEXPECTED_PEP_STATUS.format(
                    urljoin(PEP_MAIN_URL, url), page_status,
                    EXPECTED_STATUS.get(table_statuses[number])
                )
            )
    return [
        ('Статус', 'Количество'),
        *pep_status_codes.items(),
        ('Итого', str(sum(pep_status_codes.values())))
    ]


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
    try:
        configure_logging()
        logging.info(Literals.PARSER_STARTED)
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(Literals.PARSER_ARGS.format(args))
        session = CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results:
            control_output(results, args)
        logging.info(Literals.PARSER_FINISHED)
    except Exception as error:
        logging.exception(Literals.PARSER_EXCEPTION.format(error))


if __name__ == '__main__':
    main()
