import re
import sh

from .runner import Runner

class PythonRunner(Runner):

    sourcefilename = '/tmp/source.py'

    def _flake8_lint(self):
        ignore = 'F,N804,N805'
        max_line_length = 120
        output = sh.flake8('--ignore', ignore,
                           '--max-line-length', max_line_length,
                           self.sourcefilename,
                           _ok_code=self.ok_code
                          ).stdout.decode('utf-8').strip().split('\n')
        pattern = r'[\w|/]*:(?P<line>\d+):(?P<column>\d+):\s+(?P<code>[A-Z]\d+)\s+(?P<message>.*)$'
        self.response['lint'] += [re.search(pattern, line).groups() for line in output
                                  if re.search(pattern, line)]
        return

    def _pylint(self):
        disable = 'C0103,C0111,C0112,C0301,C0303,C0304'
        output = sh.pylint('--disable', disable,
                           '--reports', 'n',
                           '--msg-template', '{msg_id}:{line}:{column}:{msg}',
                           self.sourcefilename,
                           _ok_code=self.ok_code
        ).stdout.decode('utf-8').strip().split('\n')
        pattern = r'(?P<code>[A-Z]\d+):(?P<line>\d+):(?P<column>\d+):(?P<message>.*)$'
        lint = self.response['lint']
        for line in output:
            match = re.search(pattern, line)
            if match:
                lint += [(match.group('line'), match.group('column'), match.group('code'),
                          match.group('message'))]
        return

    def _radon(self):
        '''
        Collect some software metrics via radon:

            * cyclomatic_complexity
            * loc
            * halstead

        see: https://radon.readthedocs.org/en/latest/
        '''
        from radon.cli import Config
        from radon.cli.harvest import CCHarvester, RawHarvester
        from radon.metrics import h_visit

        config = Config(average=True, exclude=None, ignore=None, max='F', min='A', no_assert=True,
                        order='SCORE', show_closures=True, show_complexity=True,
                        total_average=False)
        path = [self.sourcefilename]
        cyclomatic_complexity = CCHarvester(path, config)._to_dicts()
        if cyclomatic_complexity and 'error' not in cyclomatic_complexity[self.sourcefilename]:
            self.response['cyclomatic_complexity'] = cyclomatic_complexity
        config = Config(exclude=None, ignore=None, summary=False)
        self.response['loc'] = dict(RawHarvester(path, config).results)
        self.response['halstead'] = h_visit(self.job['source'])._asdict()
        return

    def evaluate(self):
        self.response['lint'] = []
        try:
            self._pylint()
            self._flake8_lint()
            sorted(self.response['lint'], key=lambda x: (int(x[0]), int(x[1])))
            self._radon()
        except SyntaxError:
            pass
        return

    def _run_command(self):
        return ['/usr/bin/python3', self.sourcefilename]
