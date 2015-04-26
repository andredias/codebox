#!/usr/bin/python3

import re
import json

from sh import docker
from os.path import abspath, dirname, join

IMAGE = 'codebox'
CODEBOX_SOURCE_DIR = abspath(join(dirname(__file__), '../src'))
TIMEOUT = 5


def create_docker_image():
    images = str(docker.images())
    if re.search(r'\n%s\s' % IMAGE, images) is None:
        docker.build('--tag', IMAGE, CODEBOX_SOURCE_DIR)
    return


def setup():
    create_docker_image()


def run(sourcetree=None, commands=None, input_=''):
    sourcetree = sourcetree or {}
    commands = commands or []
    job = {
        'input': input_,
        'sourcetree': sourcetree,
        'commands': commands
    }
    job_json = json.dumps(job)
    output = docker.run('-i',
                        '--rm',
                        '-v', '%s:/%s_1:ro' % (CODEBOX_SOURCE_DIR, IMAGE),
                        '--workdir', '/%s_1' % IMAGE,
                        IMAGE, _in=job_json, _ok_code=[0, 1])
    return output.stderr.decode('utf-8') if output.stderr else \
        json.loads(output.stdout.decode('utf-8'))


class TestPython(object):

    filename = 'source.py'

    def run(self, source, input_=None, timeout=TIMEOUT):
        sourcetree = {self.filename: source}
        commands = [('execution', 'python3 %s' % self.filename, timeout)]
        return run(sourcetree, commands, input_)

    def test_hello_world(self):
        '''
        Program supposed to run smoothly. But no input needed
        '''
        source = 'print("Hello, World!")'
        resp = self.run(source)
        assert resp['execution']['stdout'].strip() == 'Hello, World!'
        assert resp['execution']['stderr'] == ''

    def test_program_error(self):
        '''
        Python program with a syntax error
        '''
        source = '''import os

sys.stdout.write('Olá mundo!')'''
        resp = self.run(source)
        assert resp['execution']['stdout'] == ''
        assert "NameError: name 'sys' is not defined" in resp['execution']['stderr']

    def test_empty(self):
        '''
        Running a empty source
        '''
        resp = run()
        assert resp == {}

    def test_input(self):
        text = 'Hello\nWorld'
        source = '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
        resp = self.run(source, text)
        assert resp['execution']['stdout'] == 'Hello\nWorld'
        assert resp['execution']['stderr'] == ''
        assert resp['lint'] == {}

    def test_utf_8_input(self):
        text = 'Olá\nAçúcar'
        source = '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
        resp = self.run(source, text)
        assert resp['execution']['stdout'] == 'Olá\nAçúcar'
        assert resp['execution']['stderr'] == ''
        assert resp['lint'] == {}

    def test_timeout(self):
        source = 'import time\nprint("Going to sleep...")\ntime.sleep(5)\nprint("Overslept!")'
        resp = self.run(source, timeout=0.3)
        assert resp['execution']['stdout'] == 'Going to sleep...\n'
        assert 'ERROR: Time limit exceeded' in resp['execution']['stderr']

    def test_net_access(self):
        source = 'from sh import ping\nprint(ping("-c", "1", "www.google.com"))'
        resp = self.run(source)
        assert resp['execution']['stderr'] == ''
        assert 'PING www.google.com (' in resp['execution']['stdout']

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
        resp = self.run(source)
        assert resp['execution']['stderr'] == ''
        assert 'source.py' in resp['lint']
        assert 'source.py' in resp['metrics']
        assert len(resp['lint']['source.py']) > 0
        assert isinstance(resp['metrics']['source.py']['cyclomatic_complexity'], list)
        assert len(resp['metrics']['source.py']['cyclomatic_complexity']) > 3
        assert 'source.py' not in resp['metrics']['source.py']['loc']

    def test_syntax_error(self):
        source = '''import sys
  def outer(x):
     def inner():
            print x
     return inner
'''
        resp = self.run(source)
        assert 'IndentationError: unexpected indent' in resp['execution']['stderr']
        assert 'source.py' in resp['lint']
        assert 'source.py' in resp['metrics']

    def test_access_to_worker_dir(self):
        source = 'import sh\n\nprint(sh.ls("-R", "/%s"))\n' % IMAGE
        resp = self.run(source)
        assert ('cannot open directory /%s: Permission denied' % IMAGE) in resp['execution']['stderr']

    def test_utf_8(self):
        source = 'print("Olá, açúcar, lâmpada")'
        resp = self.run(source)
        assert resp['execution']['stdout'] == 'Olá, açúcar, lâmpada\n'
        assert resp['execution']['stderr'] == ''


class TestCPP(object):

    filename = 'source.cpp'

    def run(self, source, input_=None, timeout=TIMEOUT):
        sourcetree = {self.filename: source}
        commands = [
            ('build', 'g++ %s' % self.filename, timeout),
            ('run', './a.out', timeout)
        ]
        return run(sourcetree, commands, input_)

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
        resp = self.run(source)
        assert resp['run']['stdout'] == 'Hello, world!'
        assert resp['run']['stderr'] == ''

    def test_empty_source(self):
        '''
        Running a empty source
        '''
        resp = self.run('')
        assert resp['build']['exit_code'] != 0

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
        resp = self.run(source, timeout=0.3)
        assert resp['build']['stdout'] == ''
        assert resp['build']['stderr'] == ''
        assert resp['run']['stdout'] == 'Going to sleep...'
        assert 'ERROR: Time limit exceeded' in resp['run']['stderr']

    def test_compilation_error(self):
        source = '''#include <iostream>
using std::cout;

int main() {
    string s;
    return 0;
}'''
        resp = self.run(source)
        assert 'run' not in resp
        assert 'lint' in resp
        assert resp['build']['exit_code'] == 1
        assert 'error' in resp['build']['stderr']


class TestC(object):

    filename = 'source.c'

    def run(self, source, input_=None, timeout=TIMEOUT):
        sourcetree = {self.filename: source}
        commands = [
            ('build', 'gcc %s' % self.filename, timeout),
            ('run', './a.out', timeout)
        ]
        return run(sourcetree, commands, input_)

    def test_c_code(self):
        source = '''#include <stdio.h>

int main() {
    printf("Hello, world!");
}'''
        resp = self.run(source)
        assert resp['build']['stdout'] == ''
        assert resp['build']['stderr'] == ''
        assert resp['run']['stdout'] == 'Hello, world!'
        assert resp['run']['stderr'] == ''
        assert 'lint' in resp
        assert len(resp['lint'][self.filename]) == 1


class TestRuby(object):

    filename = 'source.rb'

    def run(self, source, input_=None, timeout=TIMEOUT):
        sourcetree = {self.filename: source}
        commands = [('execution', 'ruby %s' % self.filename, timeout)]
        return run(sourcetree, commands, input_)

    def test_hello_world(self):
        source = 'puts "Hello, world!"'
        resp = self.run(source)
        assert resp['execution']['stdout'] == 'Hello, world!\n'
        assert resp['execution']['stderr'] == ''

    def test_lint(self):
        source = '''def badName
  if something
    test
    end
end'''
        resp = self.run(source)
        assert 'lint' in resp
        assert len(resp['lint'][self.filename]) >= 4


class TestJavascript(object):

    filename = 'source.js'

    def run(self, source, input_=None, timeout=TIMEOUT):
        sourcetree = {self.filename: source}
        commands = [('execution', 'nodejs %s' % self.filename, timeout)]
        return run(sourcetree, commands, input_)

    def test_hello_world(self):
        source = "console.log('Hello, world!');"
        resp = self.run(source)
        assert resp['execution']['stdout'] == 'Hello, world!\n'
        assert resp['execution']['stderr'] == ''


class TestGo(object):

    filename = 'source.go'

    def run(self, source, input_=None, timeout=TIMEOUT):
        sourcetree = {self.filename: source}
        commands = [
            ('build', 'go build -o a.out %s' % self.filename, timeout),
            ('run', './a.out', timeout)
        ]
        return run(sourcetree, commands, input_)

    def test_hello_world(self):
        source = '''package main

import "fmt"

func main() {
    fmt.Print("Hello, world!")
}'''
        resp = self.run(source)
        assert resp['build']['stdout'] == ''
        assert resp['build']['stderr'] == ''
        assert resp['run']['stdout'] == 'Hello, world!'
        assert resp['run']['stderr'] == ''


class TestSQLite(object):

    filename = 'database.db'

    def run(self, source, timeout=TIMEOUT):
        commands = [
            ('run', 'sqlite3 -bail %s' % self.filename, timeout)
        ]
        return run(commands=commands, input_=source)

    def test_help(self):
        source = '.help'
        resp = self.run(source)
        assert len(resp['run']['stderr']) > 20  # saída do .help é no stderr

    def test_simple_db(self):
        source = '''create table tbl1(one varchar(10), two smallint);
insert into tbl1 values('hello!', 10);
insert into tbl1 values('goodbye', 20);
select * from tbl1;'''
        resp = self.run(source)
        assert resp['run']['stdout'] == '''hello!|10
goodbye|20
'''

    def test_another_db(self):
        source = '''create table department(
    deptid integer primary key,
    name varchar(20),
    location varchar(10)
);

create table employee(
    empid integer primary key,
    name varchar(20),
    title varchar(10)
);

insert into employee values(101,'John Smith','CEO');
insert into employee values(102,'Raj Reddy','Sysadmin');
insert into employee values(103,'Jason Bourne','Developer');
insert into employee values(104,'Jane Smith','Sale Manager');
insert into employee values(105,'Rita Patel','DBA');

insert into department values(1,'Sales','Los Angeles');
insert into department values(2,'Technology','San Jose');
insert into department values(3,'Marketing','Los Angeles');

select * from employee;
select * from department;'''
        resp = self.run(source)
        assert resp['run']['stdout'] == '''101|John Smith|CEO
102|Raj Reddy|Sysadmin
103|Jason Bourne|Developer
104|Jane Smith|Sale Manager
105|Rita Patel|DBA
1|Sales|Los Angeles
2|Technology|San Jose
3|Marketing|Los Angeles
'''


class TestBash(object):

    filename = 'source.sh'

    def run(self, source, input_=None, timeout=TIMEOUT):
        sourcetree = {self.filename: source}
        commands = [('run', 'bash %s' % self.filename, timeout)]
        return run(sourcetree, commands, input_)

    def test_bash_1(self):
        source = "echo 'Olá mundo'"
        resp = self.run(source)
        assert resp['run']['stdout'] == 'Olá mundo\n'

    def test_ps_ax(self):
        source = 'ps ax | grep python'
        resp = self.run(source)
        assert '/usr/bin/python3 codebox.py' in resp['run']['stdout']

    def test_hg(self):
        source = 'hg version'
        resp = self.run(source)
        assert 'http://mercurial.selenic.com' in resp['run']['stdout']

    def test_git(self):
        source = 'git version'
        resp = self.run(source)
        assert source in resp['run']['stdout']

    def test_svn(self):
        source = 'svn --version'
        resp = self.run(source)
        assert 'http://subversion.apache.org/' in resp['run']['stdout']
