import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_parser, configure_logger
from constants import MAIN_DOC_URL, BASE_DIR
from handlers import find_tag
from outputs import control_output


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = session.get(whats_new_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    url_div = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = url_div.find_all('li',
                                          attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python, 'Парсим ссылочки', colour='red'):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = session.get(version_link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        results.append((version_link, h1.text,
                        dl.text.replace('\n', ' ').strip()))
    return results


def latest_versions(session):
    response = session.get(MAIN_DOC_URL)
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
    for a_tag in tqdm(a_tags, 'Собираем ссылки', colour='green'):
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = session.get(downloads_url)
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
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logger()
    logging.info('Парсер запущен')
    arg_parser = configure_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results:
        control_output(results, args)
    logging.info('Парсер завершил работу')


if __name__ == '__main__':
    main()
