import io
import os
import sh
from lint import lint
from metrics import collect_metrics

TIMEOUT_EXIT_CODE = 124


class Runner(object):

    '''
    Generic class to manage source code processing
    '''

    sourcefilename = '/tmp/sourcefile'
    execfilename = '/tmp/a.out'
    _timeout = 5
    ok_code = range(128)

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
        self.compile() and self.run()
        return self.response

    def evaluate(self):
        self.response['lint'] = lint(self.sourcefilename)
        self.response.update(collect_metrics(self.sourcefilename))
        return

    def compile(self):
        command = self._compile_command()
        if command is None:
            return True
        output = command('-o', self.execfilename, self.sourcefilename, _ok_code=self.ok_code)
        self.response['compilation'] = {
            'stdout': output.stdout.decode('utf-8'),
            'stderr': output.stderr.decode('utf-8'),
            'exit_code': output.exit_code,
        }
        return output.exit_code == 0

    def _compile_command(self):
        return None

    def run(self):
        timeout_msg = ''
        stderr = io.StringIO()
        stdout = io.StringIO()
        os.setresuid(1000, 1000, 0)  # run as 'user'
        try:
            self._run_command()(self.sourcefilename, _in=self.input, _timeout=self.timeout,
                                _encoding='utf-8', _ok_code=self.ok_code, _out=stdout, _err=stderr)
        except sh.TimeoutException:
            timeout_msg = '\nERROR: Running time limit exceeded %ss' % self.timeout
        finally:
            os.setresuid(0, 0, 0)  # back to 'root'
        self.response['execution'] = {
            'stdout': stdout.getvalue(),
            'stderr': stderr.getvalue() + timeout_msg,
        }
        return

    def _run_command(self):
        return sh.Command(self.execfilename)


class PythonRunner(Runner):

    sourcefilename = '/tmp/source.py'

    def _run_command(self):
        return sh.python3


class CPPRunner(Runner):

    sourcefilename = '/tmp/source.cpp'

    def _compile_command(self):
        return sh.Command('g++')


class CRunner(Runner):

    sourcefilename = '/tmp/source.c'

    def _compile_command(self):
        return sh.gcc


class GoRunner(Runner):

    sourcefilename = '/tmp/source.go'

    def _compile_command(self):
        return sh.go.build


class JavascriptRunner(Runner):

    sourcefilename = '/tmp/source.js'

    def _run_command(self):
        return sh.nodejs


class RubyRunner(Runner):

    sourcefilename = '/tmp/source.rb'

    def _run_command(self):
        return sh.ruby
