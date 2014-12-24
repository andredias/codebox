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

def run(source, _input=None, timeout=5, language='python'):
    job = {'input':_input, 'source':source, 'timeout':timeout, 'language':language}
    job_json = json.dumps(job)
    output = docker.run('-i',
                        '--rm',
                        '-v', '%s:/home/worker:ro' % WORKER_DIR,
                        '--net', 'none',
                        IMAGE, _in=job_json, _ok_code=[0, 1])
    return output.stdout.decode('utf-8'), output.stderr.decode('utf-8')


class TestPythonRunner(object):

    def test_hello_world(self):
        '''
        Program supposed to run smoothly. But no input needed
        '''
        source = 'print("Hello, World!")'

        out, err = run(source)
        assert out.strip() == 'Hello, World!'
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

        out, err = run(source, language='cpp')
        assert out == 'Hello, world!'
        assert err == ''

    def test_empty_source(self):
        '''
        Running a empty source
        '''
        out, err = run('', language='cpp')
        assert out == err == ''


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
        out, err = run(source, timeout=0.1, language='cpp')
        assert out == 'Going to sleep...'
        assert 'ERROR: Running time limit exceeded' in err


class TestCRunner(object):

    def test_c_code(self):
        source = '''#include <stdio.h>

int main() {
    printf("Hello, world!");
}'''
        out, err = run(source, language='c')
        assert out == 'Hello, world!'
        assert err == ''


class TestRubyRunner(object):

    def test_hello_world(self):
        source = 'puts "Hello, world!"'
        out, err = run(source, language='ruby')
        assert out == 'Hello, world!\n'
        assert err == ''


class TestJavascriptRunner(object):

    def test_hello_world(self):
        source = "console.log('Hello, world!');"
        out, err = run(source, language='javascript')
        assert out == 'Hello, world!\n'
        assert err == ''


class TestGoRunner(object):

    def test_hello_world(self):
        source = '''package main

import "fmt"

func main() {
    fmt.Print("Hello, world!")
}'''
        out, err = run(source, language='go')
        assert out == 'Hello, world!'
        assert err == ''

