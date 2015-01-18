#!/usr/bin/python3

import re
import json

from sh import docker
from os.path import abspath, dirname, join

IMAGE = 'codebox'
WORKER_DIR = abspath(join(dirname(__file__), '../worker'))


def create_docker_image():
    images = str(docker.images())
    if re.search(r'\ncodebox\s', images) is None:
        docker.build('--tag', IMAGE, WORKER_DIR)
    return


def setup():
    create_docker_image()


def run(source, _input=None, timeout=5, language='python'):
    job = {'input': _input, 'source': source, 'timeout': timeout, 'language': language}
    job_json = json.dumps(job)
    output = docker.run('-i',
                        '--rm',
                        '-v', '%s:/codebox_1:ro' % WORKER_DIR,
                        '--workdir', '/codebox_1',
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

    def test_input(self):
        text = 'Hello\nWorld'
        source = '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
        resp = run(source, text)
        assert resp['execution']['stdout'] == 'Hello\nWorld'
        assert resp['execution']['stderr'] == ''
        assert resp['lint'] == []

    def test_utf_8_input(self):
        text = 'Olá\nAçúcar'
        source = '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
        resp = run(source, text)
        assert resp['execution']['stdout'] == 'Olá\nAçúcar'
        assert resp['execution']['stderr'] == ''
        assert resp['lint'] == []

    def test_timeout(self):
        source = 'import time\nprint("Going to sleep...")\ntime.sleep(5)\nprint("Overslept!")'
        resp = run(source, timeout=0.2)
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
        assert 'cyclomatic_complexity' in resp
        assert 'loc' in resp
        assert 'halstead' in resp
        assert 'lint' in resp
        assert len(resp['lint']) > 10

    def test_syntax_error(self):
        source = '''import sys
  def outer(x):
     def inner():
            print x
     return inner
'''
        resp = run(source)
        assert 'IndentationError: unexpected indent' in resp['execution']['stderr']
        assert 'cyclomatic_complexity' in resp
        assert 'loc' in resp
        assert len(resp['lint']) > 0

    def test_access_to_codebox_dir(self):
        source = 'import sh; print(sh.ls("/codebox"))'
        resp = run(source)
        assert 'cannot open directory /codebox: Permission denied' in resp['execution']['stderr']

    def test_utf_8(self):
        source = 'print("Olá, açúcar, lâmpada")'
        resp = run(source)
        assert resp['execution']['stdout'] == 'Olá, açúcar, lâmpada\n'
        assert resp['execution']['stderr'] == ''
        assert 'error' not in list(resp['loc'].values())[0].keys()


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

    def test_timeout(self):
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

    def test_compilation_error(self):
        source = '''#include <iostream>
using std::cout;

int main() {
    string s;
    return 0;
}'''
        resp = run(source, language='cpp')
        assert 'execution' not in resp
        assert 'lint' in resp
        assert resp['compilation']['exit_code'] == 1
        assert 'error' in resp['compilation']['stderr']


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
        assert 'lint' in resp
        assert len(resp['lint']) == 1


class TestRubyRunner(object):

    def test_hello_world(self):
        source = 'puts "Hello, world!"'
        resp = run(source, language='ruby')
        assert resp['execution']['stdout'] == 'Hello, world!\n'
        assert resp['execution']['stderr'] == ''

    def test_lint(self):
        source = '''def badName
  if something
    test
    end
end'''
        resp = run(source, language='ruby')
        assert 'lint' in resp
        assert len(resp['lint']) >= 4


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
