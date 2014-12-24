#!/usr/bin/python3

import sh
import sys
import json

TIMEOUT_EXIT_CODE = 124

class Runner(object):

    '''
    Generic class to manage source code processing
    '''

    sourcefilename = '/tmp/source'
    _timeout = 5
    ok_code = list(range(128))  # sh does not work with python3 range yet

    def __call__(self, job):
        _input = job.get('input', None)
        self.timeout = job.get('timeout', self._timeout)
        # save source to a temporary file for compiling and running it later
        with open(self.sourcefilename, mode='w', encoding='utf-8') as sourcefile:
            sourcefile.write(job['source'])
            sourcefile.flush()
        output = sh.timeout('--foreground', self.timeout, *self._run_command(), _in=_input,
                            _ok_code=self.ok_code)
        if output is not None:
            sys.stdout.write(output.stdout.decode('utf-8'))
            sys.stderr.write(output.stderr.decode('utf-8'))
            if output.exit_code == TIMEOUT_EXIT_CODE:
                sys.stderr.write('\nERROR: Running time limit exceeded %ss' % self.timeout)
        return


class PythonRunner(Runner):

    sourcefilename = '/tmp/source.py'

    def _run_command(self):
        return ['/usr/bin/python3', self.sourcefilename]


if __name__ == '__main__':
    py_runner = PythonRunner()
    py_runner(json.load(sys.stdin))
