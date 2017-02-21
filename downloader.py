import urllib.parse
import urllib.request
import re
import html.parser
import shutil
import os


class MyHTMLParser(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.download_list = []

    def handle_starttag(self, tag, attrs):
        if tag != 'input' or not ('value', 'Download') in attrs:
            return

        for attr in attrs:
            if attr[0] == 'onclick':
                self.download_list.append(extract_software_hash(attr[1]))

    def error(self, message):
        pass


def create_download_link(url, path):
    parsed_url = urllib.parse.urlparse(url)
    return urllib.parse.urljoin(''.join([parsed_url.scheme, '://', parsed_url.netloc, parsed_url.path]), path)


def extract_software_hash(text):
    try:
        return re.search('.\'(.+?)\'', text).group(1)
    except AttributeError:
        print('Couldn\'t construct download link!')


def validate_file_size(filename, expected_size):
    size = os.path.getsize(filename)
    if size != expected_size:
        raise Exception('Incomplete download! Downloaded ' + str(size) + ' but expected: ' + str(expected_size))


def download_file(url, filename):
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def get_download_data(path):
    download_link = create_download_link(target_url, path)
    res = urllib.request.urlopen(download_link)
    res.close()
    return res.geturl(), int(res.getheader('content-length'))

target_url = input('Enter target URL: ')

print('Analysing source...')
source_html = urllib.request.urlopen(target_url).read()

parser = MyHTMLParser()
parser.feed(source_html.decode("utf-8"))

files_amount = len(parser.download_list)

print('Found ' + str(files_amount) + ' files')

current = 0

for path in parser.download_list:
    final_url, file_size = get_download_data(path)
    filename = urllib.parse.urlparse(final_url).path.split('/')[-1]

    print('Downloading ' + filename + ' (' + str(file_size) + ' bytes)')

    download_file(final_url, filename)
    validate_file_size(filename, file_size)
    current += 1

    print('File ' + filename + ' downloaded successfully! (' + str(current) + '/' + str(files_amount) + ')')
