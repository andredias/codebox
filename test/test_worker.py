#!/usr/bin/python3

import re
import sh
import json

from sh import docker
from os.path import abspath, dirname, join

IMAGE = 'codebox'
WORKER_DIR = abspath(join(dirname(__file__), '../worker'))

def CreateDockerImage():
    images = str(docker.images())
    if re.search('\ncodebox\s', images) is None:
        docker.build('--tag', IMAGE, WORKER_DIR)
    return

def setup():
    CreateDockerImage()

def run(source, _input=None, timeout=5):
    job = {'input':_input, 'source':source, 'timeout':timeout}
    job_json = json.dumps(job)
    output = docker.run('-i',
                        '--rm',
                        '-v', '%s:/home/worker' % WORKER_DIR,
                        '--net', 'none',
                        IMAGE, _in=job_json, _ok_code=[0, 1])
    return output.stdout.decode('utf-8'), output.stderr.decode('utf-8')


class TestPythonRunner(object):

    def test_program_ok(self):
        '''
        Program supposed to run smoothly. But no input needed
        '''
        source = '''
def double(x):
    return 2*x

print(double(7))'''

        out, err = run(source)
        assert out.strip() == '14'
        assert err == ''

    def test_program_error(self):
        '''
        Python program with a syntax error
        '''
        source = '''import os

sys.stdout.write('Olá mundo!')'''
        out, err = run(source)
        assert out == ''
        assert "NameError: name 'sys' is not defined" in err

    def test_empty_source(self):
        '''
        Running a empty source
        '''
        out, err = run('')
        assert out == err == ''

    def test_process_input(self):
        text = 'Hello\nWorld'
        source = '''
#!/usr/bin/python3

import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
        out, err = run(source, text)
        assert out == 'Hello\nWorld'
        assert err == ''

    def test_process_timeout(self):
        source = 'import time\nprint("Going to sleep...")\ntime.sleep(5)\nprint("Overslept!")'
        out, err = run(source, timeout=0.1)
        assert out == 'Going to sleep...\n'
        assert 'ERROR: Running time limit exceeded' in err

    def test_net_access(self):
        source = 'from sh import ping\nprint(ping("www.google.com"))'
        out, err = run(source)
        assert out == ''
        assert 'ping: unknown host www.google.com' in err
