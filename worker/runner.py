import io
import os
import re
import sh
from tempfile import mkdtemp
from lint import lint
from metrics import collect_metrics

TIMEOUT_EXIT_CODE = 124


class Runner(object):

    '''
    Generic class to manage source code processing
    '''

    ok_code = range(128)

    def __call__(self, job):
        '''
        job = {'input': _input, 'sourcetree': {filename:source, ...}, 'commands': [command, command...]}
        command = (phase, line, timeout)
        '''

        if 'sourcetree' not in job or not job['sourcetree']:
            return {}
        self.job = job
        self.response = {}
        self.input = job.get('input')
        os.setresuid(1000, 1000, 0)  # run as 'user'
        try:
            self.tempdir = mkdtemp()
            os.chdir(self.tempdir)
            self.save_sourcetree()
            self.collect_metrics()
            self.exec_commands()
        finally:
            os.setresuid(0, 0, 0)  # back to 'root'
        return self.response

    def save_sourcetree(self):
        '''
        Save sources to a temporary directory
        '''
        for name, source in self.job['sourcetree'].items():
            filename = os.path.join(self.tempdir, name)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, mode='w', encoding='utf-8') as f:
                f.write(source)

    def collect_metrics(self):
        self.result['lint'] = {}
        self.result['metrics'] = {}
        for filename in self.job['sourcetree'].keys():
            tempfilename = os.path.join(self.tempdir, filename)
            result = lint(tempfilename)
            if result:
                self.result['lint'][filename] = result
            result = collect_metrics(tempfilename)
            if result:
                self.result['metrics'][filename] = result
        return

    def exec_commands(self):
        for phase, command, timeout in self.job['commands']:
            command, *args = re.sub(r'\s+', ' ', command).split()  # *args não funciona no python2
            command = sh.Command(command)
            timeout_msg = ''
            stdout = io.StringIO()
            stderr = io.StringIO()
            try:
                output = command(*args, _in=self.input, _timeout=timeout, _encoding='utf-8',
                                 _ok_code=self.ok_code, _out=stdout, _err=stderr)
            except sh.TimeoutException:
                timeout_msg = '\nERROR: Time limit exceeded %ss' % timeout
            self.response[phase] = {
                'stdout': stdout.getvalue(),
                'stderr': stderr.getvalue() + timeout_msg,
                'exit_code': output.exit_code,
            }
            if output.exit_code != 0:
                break


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


class SQLiteRunner(Runner):

    sourcefilename = '/tmp/source.sql'

    def _run_command(self):
        self.input = self.job['source']
        self.sourcefilename = '/tmp/database.db'
        self.command_options = ['-bail']
        return sh.sqlite3


class BashRunner(Runner):

    sourcefilename = '/tmp/source.sh'

    def _run_command(self):
        return sh.bash
