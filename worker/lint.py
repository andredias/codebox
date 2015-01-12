'''
Line and column of lint messages should start at 1, not 0.

Each lint result should have the following fields:

    * line: integer, starting at 1
    * column: integer, starting at 1
    * message: string
    * level: 'error', 'warning' or 'info'.
    * linter: name of the program used
'''

import re
import sh
import json
import lint_messages as lm
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
            result += [
                {
                'line': int(match.group('line')),
                'column': int(match.group('column')),
                'code': match.group('code'),
                'message': match.group('message'),
                'level': lm.flake8.get(match.group('code'), 'info'),
                'linter': 'flake8',
                }
            ]

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
            result += [
                {
                'line': int(match.group('line')),
                'column': int(match.group('column')) + 1,  # column should start at 1, not 0
                'code': match.group('code'),
                'message': match.group('message'),
                'level': lm.pylint.get(match.group('code'), 'info'),
                'linter': 'pylint',
                }
            ]
    return result


def cpplint(filename):
    linter = join(dirname(__file__), 'cpplint.py')
    reports = sh.Command(linter)('--linelength', '120', '--filter=-legal', filename, _ok_code=ok_codes)
    pattern = r'^[\w\d\.\-_/]+:(?P<line>\d+):\s+(?P<msg>(?:(?!\s+\[).)+)\s+\[(?P<code>[\w\d/]+)'
    result = []
    for line in reports.stderr.decode('utf-8').split('\n'):
        match = re.findall(pattern, line)
        if match:
            match = match[0]
            result += [
                {
                'line': int(match[0]),
                'code': match[2],
                'message': match[1],
                'level': lm.cpplint.get(match[2], 'info'),
                'linter': 'cpplint',
                }
            ]
    return result


def flintplusplus(filename, c_flag=''):
    linter = join(dirname(__file__), 'flint++')
    reports = sh.Command(linter)('-j', c_flag, filename, _ok_code=ok_codes)
    reports = json.loads(str(reports))
    reports = reports['files'][0]['reports']
    return [
        {
        'line': r['line'],
        'code': r['title'],
        'message': r['desc'],
        'level': r['level'],
        'linter': 'flint++',
        }
        for r in reports]


def rubocop(filename):
    '''
    RuboCop (https://github.com/bbatsov/rubocop) is a Ruby static code analyzer.
    Out of the box it will enforce many of the guidelines outlined in
    the community Ruby Style Guide (https://github.com/bbatsov/ruby-style-guide).

    $ rubocop --format simple test.rb
    == test.rb ==
    C:  1:  1: Use snake_case for methods and variables.
    C:  2:  3: Favor modifier if/unless usage when you have a single-line body...
    W:  4:  5: end at 4, 4 is not aligned with if at 2, 2

    1 file inspected, 3 offenses detected
    '''
    reports = str(sh.rubocop('--format', 'simple', filename, _ok_code=ok_codes)).split('\n')
    pattern = r'^(?P<code>\w):\s+(?P<line>\d+):\s+(?P<column>\d+):\s+(?P<message>.*)$'
    code = {'R': 'Refactor', 'C': 'Convention', 'E': 'Error', 'F': 'Fatal', 'W': 'Warning'}
    result = []
    for line in reports:
        match = re.search(pattern, line)
        if match:
            result += [
                {
                'line': int(match.group('line')),
                'column': int(match.group('column')),
                'code': code[match.group('code')],
                'message': match.group('message'),
                'level': lm.rubocop.get(match.group('code'), 'info'),
                'linter': 'rubocop',
                }
            ]
    return result


linters = {
    '.py': (flake8, pylint),
    '.cpp': (cpplint, flintplusplus),
    '.hpp': (cpplint, flintplusplus),
    '.c': (cpplint, lambda x: flintplusplus(x, c_flag='-c')),
    '.h': (cpplint, lambda x: flintplusplus(x, c_flag='-c')),
    '.rb': (rubocop, ),
}


# TODO: classify lint messages into type 'error', 'warning' or 'info'

def lint(filename):
    extension = splitext(filename)[1]
    result = []
    for linter in linters.get(extension, []):
        try:
            result += linter(filename)
        except:
            traceback.print_exc()
    result.sort(key=lambda x: (x['line'], x.get('column', 0), x['code']))
    return result
