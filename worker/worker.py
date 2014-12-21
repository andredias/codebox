#!/usr/bin/python3

import sh
import sys
import json
from tempfile import NamedTemporaryFile


class Runner(object):

    '''
    Generic class to manage source code processing
    '''

    def __init__(self, filename):
        self.filename = filename
        self.output = None
        return

    def _write(self):
        sys.stdout.write(self.output.stdout.decode('utf-8'))
        sys.stderr.write(self.output.stderr.decode('utf-8'))
        return

    def run(self, _input=None):
        self.output = self._run(_input)
        if self.output is not None:
            self._write()
        return

    def _run(self, _input=None):
        raise NotImplementedError()


class PythonRunner(Runner):

    def _run(self, _input=None):
        return sh.python3(self.filename, _in=_input, _ok_code=[0, 1])

    def _collect_metrics(self):
        pass


def work(job):
    with NamedTemporaryFile(mode='w', encoding='utf-8') as sourcefile:
        sourcefile.write(job['source'])
        sourcefile.flush()
        PythonRunner(sourcefile.name).run(job['input'])
    return


if __name__ == '__main__':
    work(json.load(sys.stdin))
