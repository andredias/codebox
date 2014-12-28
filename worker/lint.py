import re
import sh
import json
import traceback
from os.path import dirname, join, splitext

ok_codes = list(range(128))

def flake8(filename):
    ignore = 'F,N804,N805'
    max_line_length = 120
    output = sh.flake8('--ignore', ignore,
                       '--max-line-length', max_line_length, filename,
                       _ok_code=ok_codes).stdout.decode('utf-8').strip().split('\n')
    pattern = r'[\w|/]*:(?P<line>\d+):(?P<column>\d+):\s+(?P<code>[A-Z]\d+)\s+(?P<message>.*)$'
    result = []
    for line in output:
        match = re.search(pattern, line)
        if match:
            result += [(int(match.group('line')), match.group('code'), match.group('message'))]
    return result


def pylint(filename):
    disable = 'C0103,C0111,C0112,C0301,C0303,C0304'
    output = sh.pylint('--disable', disable,
                       '--reports', 'n',
                       '--msg-template', '{msg_id}:{line}:{column}:{msg}',
                       filename,
                       _ok_code=ok_codes).stdout.decode('utf-8').strip().split('\n')
    pattern = r'(?P<code>[A-Z]\d+):(?P<line>\d+):(?P<column>\d+):(?P<message>.*)$'
    result = []
    for line in output:
        match = re.search(pattern, line)
        if match:
            result += [(int(match.group('line')), match.group('code'), match.group('message'))]
    return result


def cpplint(filename):
    linter = join(dirname(__file__), 'cpplint.py')
    lint = sh.Command(linter)('--linelength', '120', '--filter=-legal', filename, _ok_code=ok_codes)
    pattern = r'^[\w\d\.\-_/]+:(?P<line>\d+):\s+(?P<msg>(?:(?!\s+\[).)+)\s+\[(?P<code>[\w\d/]+)'
    result = []
    for line in lint.stderr.decode('utf-8').split('\n'):
        match = re.findall(pattern, line)
        if match:
            match = match[0]
            result += [(int(match[0]), match[2], match[1])]
    return result


def flintplusplus(filename):
    linter = join(dirname(__file__), 'flint++')
    lint = sh.Command(linter)('-j', filename, _ok_code=ok_codes)
    lint = json.loads(str(lint))
    reports = lint['files'][0]['reports']
    return [(r['line'], r['title'], r['desc'], r['level']) for r in reports]


linters = {
    '.py': (flake8, pylint),
    '.cpp': (cpplint, flintplusplus),
}


def lint(filename):
    extension = splitext(filename)[1]
    result = []
    for linter in linters.get(extension, []):
        try:
            result += linter(filename)
        except:
            traceback.print_exc()
    return result
