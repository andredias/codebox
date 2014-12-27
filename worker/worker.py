#!/usr/bin/python3

import os
import re
import sh
import sys
import json

TIMEOUT_EXIT_CODE = 124


class Runner(object):

    '''
    Generic class to manage source code processing
    '''

    sourcefilename = '/tmp/sourcefile'
    execfilename = '/tmp/a.out'
    _timeout = 5
    ok_code = list(range(128))  # sh does not work with python3 range yet

    def __call__(self, job):
        if not job['source']:
            return {}
        self.job = job
        self.response = {}
        self.input = job.get('input', None)
        self.timeout = job.get('timeout', self._timeout)
        # save source to a temporary file for compiling and running it later
        with open(self.sourcefilename, mode='w', encoding='utf-8') as sourcefile:
            sourcefile.write(job['source'])
        self.evaluate()
        self.compile()
        self.run()
        return self.response

    def evaluate(self):
        pass

    def compile(self):
        command = self._compile_command()
        if command is None:
            return
        output = command('-o', self.execfilename, self.sourcefilename, _ok_code=self.ok_code)
        self.response['compilation'] = {
            'stdout': output.stdout.decode('utf-8'),
            'stderr': output.stderr.decode('utf-8'),
            'exit_code': output.exit_code,
        }
        return

    def _compile_command(self):
        return None

    def run(self):
        os.setresuid(1000, 1000, 0)  # run as 'user'
        try:
            output = sh.timeout('--foreground', self.timeout, *self._run_command(), _in=self.input,
                                _ok_code=self.ok_code)
        finally:
            os.setresuid(0, 0, 0)  # back to 'root'
        timeout_msg = ''
        if output.exit_code == TIMEOUT_EXIT_CODE:
            timeout_msg = '\nERROR: Running time limit exceeded %ss' % self.timeout
        self.response['execution'] = {
            'stdout': output.stdout.decode('utf-8'),
            'stderr': output.stderr.decode('utf-8') + timeout_msg,
            'exit_code': output.exit_code,
        }
        return

    def _run_command(self):
        return [self.execfilename]


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


class GoRunner(Runner):

    sourcefilename = '/tmp/source.go'

    def _compile_command(self):
        return sh.go.build


class CPPRunner(Runner):

    sourcefilename = '/tmp/source.cpp'

    def _compile_command(self):
        return sh.Command('clang++')


class CRunner(Runner):

    sourcefilename = '/tmp/source.c'

    def _compile_command(self):
        return sh.clang


class JavascriptRunner(Runner):

    sourcefilename = '/tmp/source.js'

    def _run_command(self):
        return ['nodejs', self.sourcefilename]


class RubyRunner(Runner):

    sourcefilename = '/tmp/source.rb'

    def _run_command(self):
        return ['ruby', self.sourcefilename]


languages = {
    'c': CRunner,
    'cpp': CPPRunner,
    'go': GoRunner,
    'javascript': JavascriptRunner,
    'python': PythonRunner,
    'ruby': RubyRunner,
}


if __name__ == '__main__':
    linhas = ''.join(sys.stdin.readlines())
    entrada = json.loads(linhas)
    if entrada['language'] not in languages:
        sys.exit('There is no Runner class for %s' % entrada['language'])
    runner = languages[entrada['language']]()
    response = runner(entrada)
    json.dump(response, sys.stdout)
    sys.exit(0)
