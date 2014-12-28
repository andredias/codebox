import re
import sh
import json
from .runner import Runner


class CPPRunner(Runner):

    sourcefilename = '/tmp/source.cpp'

    def evaluate(self):
        self.response['lint'] = []
        # cpplint.py
        lint = sh.Command('./cpplint.py')('--linelength', '120', '--filter=-legal',
                                           self.sourcefilename, _ok_code=[0, 1])
        pattern = r'^[\w\d\.\-_/]+:(?P<line>\d+):\s+(?P<msg>(?:(?!\s+\[).)+)\s+\[(?P<code>[\w\d/]+)'
        for line in lint.stderr.decode('utf-8').split('\n'):
            match = re.findall(pattern, line)
            if match:
                match = match[0]
                self.response['lint'] += [(int(match[0]), match[2], match[1])]
        # flint++
        lint = sh.Command('./flint++')('-j', self.sourcefilename, _ok_code=[0, 1])
        lint = json.loads(str(lint))
        reports = lint['files'][0]['reports']
        self.response['lint'] += [(r['line'], r['title'], r['desc'], r['level']) for r in reports]
        return

    def _compile_command(self):
        return sh.Command('clang++')


class CRunner(Runner):

    sourcefilename = '/tmp/source.c'

    def _compile_command(self):
        return sh.clang
