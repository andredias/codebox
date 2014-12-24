#!/usr/bin/python3

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
        self.input = job.get('input', None)
        self.timeout = job.get('timeout', self._timeout)
        # save source to a temporary file for compiling and running it later
        with open(self.sourcefilename, mode='w', encoding='utf-8') as sourcefile:
            sourcefile.write(job['source'])
        self.evaluate()
        self.compile()
        self.run()
        return

    def evaluate(self):
        pass

    def compile(self):
        command = self._compile_command()
        if command is None:
            return
        output = command('-o', self.execfilename, self.sourcefilename, _ok_code=self.ok_code)
        if output is not None:
            sys.stdout.write(output.stdout.decode('utf-8'))
            sys.stderr.write(output.stderr.decode('utf-8'))
        return

    def _compile_command(self):
        return None

    def run(self):
        output = sh.timeout('--foreground', self.timeout, *self._run_command(), _in=self.input,
                            _ok_code=self.ok_code)
        if output is not None:
            sys.stdout.write(output.stdout.decode('utf-8'))
            sys.stderr.write(output.stderr.decode('utf-8'))
            if output.exit_code == TIMEOUT_EXIT_CODE:
                sys.stderr.write('\nERROR: Running time limit exceeded %ss' % self.timeout)
        return

    def _run_command(self):
        return [self.execfilename]


class PythonRunner(Runner):

    sourcefilename = '/tmp/source.py'

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
    if not entrada.get('source', None):
        sys.exit(0)
    if entrada['language'] not in languages:
        sys.exit('There is no Runner class for %s' % entrada['language'])
    runner = languages[entrada['language']]()
    runner(entrada)
