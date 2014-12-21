#!/usr/bin/python3

import sh
import sys
import json
from tempfile import NamedTemporaryFile

TIMEOUT = 5
TIMEOUT_EXIT_CODE = 124

class Runner(object):

    '''
    Generic class to manage source code processing
    '''

    def __call__(self, job):
        _input = job.get('input', None)
        self.timeout = job.get('timeout', TIMEOUT)
        # save source to a temporary file for compiling and running it later
        self.sourcefile = NamedTemporaryFile(mode='w', encoding='utf-8')
        self.sourcefile.write(job['source'])
        self.sourcefile.flush()
        output = sh.timeout('--foreground', self.timeout, *self._run_command(), _in=_input,
                            _ok_code=[0, 1, TIMEOUT_EXIT_CODE])
        if output is not None:
            sys.stdout.write(output.stdout.decode('utf-8'))
            sys.stderr.write(output.stderr.decode('utf-8'))
            if output.exit_code == TIMEOUT_EXIT_CODE:
                sys.stderr.write('\nERROR: Running time limit exceeded %ss' % self.timeout)
        return


class PythonRunner(Runner):

    def _run_command(self):
        return ['/usr/bin/python3', self.sourcefile.name]


if __name__ == '__main__':
    py_runner = PythonRunner()
    py_runner(json.load(sys.stdin))
