#!/usr/bin/python3

import re
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


def run(source, _input=None, timeout=5, language='python'):
    job = {'input': _input, 'source': source, 'timeout': timeout, 'language': language}
    job_json = json.dumps(job)
    output = docker.run('-i',
                        '--rm',
                        '-v', '%s:/home/worker:ro' % WORKER_DIR,
                        '--net', 'none',
                        IMAGE, _in=job_json, _ok_code=[0, 1])
    return output.stderr.decode('utf-8') if output.stderr else \
           json.loads(output.stdout.decode('utf-8'))


class TestPythonRunner(object):

    def test_hello_world(self):
        '''
        Program supposed to run smoothly. But no input needed
        '''
        source = 'print("Hello, World!")'

        resp = run(source)
        assert resp['execution']['stdout'].strip() == 'Hello, World!'
        assert resp['execution']['stderr'] == ''

    def test_program_error(self):
        '''
        Python program with a syntax error
        '''
        source = '''import os

sys.stdout.write('Olá mundo!')'''
        resp = run(source)
        assert resp['execution']['stdout'] == ''
        assert "NameError: name 'sys' is not defined" in resp['execution']['stderr']

    def test_empty_source(self):
        '''
        Running a empty source
        '''
        resp = run('')
        assert resp == {}

    def test_process_input(self):
        text = 'Hello\nWorld'
        source = '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
        resp = run(source, text)
        assert resp['execution']['stdout'] == 'Hello\nWorld'
        assert resp['execution']['stderr'] == ''
        assert resp['lint'] == []

    def test_process_timeout(self):
        source = 'import time\nprint("Going to sleep...")\ntime.sleep(5)\nprint("Overslept!")'
        resp = run(source, timeout=0.1)
        assert resp['execution']['stdout'] == 'Going to sleep...\n'
        assert 'ERROR: Running time limit exceeded' in resp['execution']['stderr']

    def test_net_access(self):
        source = 'from sh import ping\nprint(ping("www.google.com"))'
        resp = run(source)
        assert resp['execution']['stdout'] == ''
        assert 'ping: unknown host www.google.com' in resp['execution']['stderr']

    def test_evaluation(self):
        source = '''import sys

def outer(x):
     def inner():
            print(x)
     return inner

class someclass():

    def wrongMethod():
        aux = None
        return
'''
        resp = run(source)
        assert resp['execution']['stderr'] == ''
        assert 'cyclomatic_complexity' not in resp
        assert 'loc' in resp
        assert 'halstead' in resp
        assert [x[2] for x in resp['lint'] if len(x[2]) == 5]  # pylint error
        assert [x[2] for x in resp['lint'] if len(x[2]) == 4]  # flake8 error

    def test_syntax_error(self):
        source = '''import sys
  def outer(x):
     def inner():
            print x
     return inner
'''
        resp = run(source)
        assert 'IndentationError: unexpected indent' in resp['execution']['stderr']
        assert 'cyclomatic_complexity' not in resp
        assert 'loc' in resp
        assert [x[2] for x in resp['lint'] if len(x[2]) == 5]  # pylint error
        assert [x[2] for x in resp['lint'] if len(x[2]) == 4]  # flake8 error


class TestCPPRunner(object):

    def test_hello_world(self):
        '''
        Program supposed to run smoothly. But no input needed
        '''
        source = '''#include <iostream>
using namespace std;

int main() {
    cout << "Hello, world!";
    return 0;
}'''

        resp = run(source, language='cpp')
        assert resp['execution']['stdout'] == 'Hello, world!'
        assert resp['execution']['stderr'] == ''

    def test_empty_source(self):
        '''
        Running a empty source
        '''
        resp = run('', language='cpp')
        assert resp == {}

    def test_process_timeout(self):
        source = '''
#include <iostream>
using namespace std;

int main() {
    cout << "Going to sleep..." << flush;
    while (1) {
    }
    cout << "overslept!";
    return 0;
}'''
        resp = run(source, timeout=0.1, language='cpp')
        assert resp['compilation']['stdout'] == ''
        assert resp['compilation']['stderr'] == ''
        assert resp['execution']['stdout'] == 'Going to sleep...'
        assert 'ERROR: Running time limit exceeded' in resp['execution']['stderr']


class TestCRunner(object):

    def test_c_code(self):
        source = '''#include <stdio.h>

int main() {
    printf("Hello, world!");
}'''
        resp = run(source, language='c')
        assert resp['compilation']['stdout'] == ''
        assert resp['compilation']['stderr'] == ''
        assert resp['execution']['stdout'] == 'Hello, world!'
        assert resp['execution']['stderr'] == ''


class TestRubyRunner(object):

    def test_hello_world(self):
        source = 'puts "Hello, world!"'
        resp = run(source, language='ruby')
        assert resp['execution']['stdout'] == 'Hello, world!\n'
        assert resp['execution']['stderr'] == ''


class TestJavascriptRunner(object):

    def test_hello_world(self):
        source = "console.log('Hello, world!');"
        resp = run(source, language='javascript')
        assert resp['execution']['stdout'] == 'Hello, world!\n'
        assert resp['execution']['stderr'] == ''


class TestGoRunner(object):

    def test_hello_world(self):
        source = '''package main

import "fmt"

func main() {
    fmt.Print("Hello, world!")
}'''
        resp = run(source, language='go')
        assert resp['compilation']['stdout'] == ''
        assert resp['compilation']['stderr'] == ''
        assert resp['execution']['stdout'] == 'Hello, world!'
        assert resp['execution']['stderr'] == ''
