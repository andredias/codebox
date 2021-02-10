from os.path import exists, join
from pathlib import Path

from app.codebox import save_sources  # isort:skip

TIMEOUT = 0.1


def test_save_sources(tmp_path: Path) -> None:
    sources = {
        'a': 'aaaa',
        'b': 'bbb',
        'app/d': 'ddd',
        'app/x/e': 'eee',
        'images/f': 'fff',
        '/images/g': 'ggg',
    }
    save_sources(tmp_path, sources)
    assert len(list(tmp_path.glob('**/*'))) == 9


def test_evaluate():
    sourcetree = {
        'source.py': '''import sys

def outer(x):
     def inner():
            print(x)
     return inner

class someclass():

    def wrongMethod():
        aux = None
        return
''',
    }
    tempdir = '/tmp/test_evaluate'
    save_sources(sourcetree, tempdir)
    result = codebox.evaluate(sourcetree, tempdir)
    assert 'source.py' in result['lint']
    assert 'source.py' in result['metrics']
    assert len(result['lint']['source.py']) > 0
    assert isinstance(result['metrics']['source.py']['cyclomatic_complexity'], list)
    assert 'source.py' not in result['metrics']['source.py']['loc']


def test_exec_command_1():
    commands = [('hello', 'echo 1 2 3', TIMEOUT)]
    result = codebox.exec_commands(commands)
    assert 'hello' in result
    assert result['hello']['stdout'] == '1 2 3\n'
    assert result['hello']['exit_code'] == 0


def test_exec_python_hello():
    sourcetree = {
        'hello.py': 'import sys\n\nprint("Hello, world!")',
    }
    tempdir = '/tmp/test_exec_python_hello'
    save_sources(sourcetree, tempdir)
    command = [('exec', 'python3 hello.py', TIMEOUT)]
    result = codebox.exec_commands(command, ref_dir=tempdir)
    assert 'exec' in result
    assert result['exec']['stdout'] == 'Hello, world!\n'
    assert result['exec']['exit_code'] == 0


def test_program_error():
    '''
    Python program with a syntax error
    '''
    source = '''import os

sys.stdout.write('Olá mundo!')'''
    sourcetree = {'hello.py': source}
    tempdir = 'test_program_error'
    save_sources(sourcetree, tempdir)
    command = [
        ('execution', 'python3 hello.py', TIMEOUT),
    ]
    resp = codebox.exec_commands(command, ref_dir=tempdir)
    assert resp['execution']['stdout'] == ''
    assert "NameError: name 'sys' is not defined" in resp['execution']['stderr']
    assert resp['execution']['exit_code'] != 0


def test_empty_source():
    '''
    Running a empty source
    '''
    sourcetree = {'empty.py': ''}
    tempdir = '/tmp/test_empty_source'
    save_sources(sourcetree, tempdir)
    command = [('execution', 'python3 empty.py', TIMEOUT)]
    resp = codebox.exec_commands(command, ref_dir=tempdir)
    assert resp == {'execution': {'stderr': '', 'exit_code': 0, 'stdout': ''}}


def test_empty_command():
    '''
    Running empty commands
    '''
    resp = codebox.exec_commands([])
    assert resp == {}


def test_input():
    text = 'Hello\nWorld'
    source = '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
    sourcetree = {
        'input.py': source,
    }
    tempdir = '/tmp/test_input'
    save_sources(sourcetree, tempdir)
    command = [('test_input', 'python3 input.py', TIMEOUT)]
    resp = codebox.exec_commands(command, input_=text, ref_dir=tempdir)
    assert resp['test_input']['stdout'] == 'Hello\nWorld'
    assert resp['test_input']['stderr'] == ''


def test_utf_8_input():
    text = 'Olá\nAçúcar'
    source = '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
    sourcetree = {
        'input.py': source,
    }
    tempdir = '/tmp/test_utf_8_input'
    save_sources(sourcetree, tempdir)
    command = [('utf_8', 'python3 input.py', TIMEOUT)]
    resp = codebox.exec_commands(command, input_=text, ref_dir=tempdir)
    assert resp['utf_8']['stdout'] == 'Olá\nAçúcar'
    assert resp['utf_8']['stderr'] == ''


def test_timeout():
    source = 'import time\nprint("Going to sleep...")\ntime.sleep(5)\nprint("Overslept!")'
    sourcetree = {
        'timeout.py': source
    }
    tempdir = '/tmp/test_timeout'
    save_sources(sourcetree, tempdir)
    command = [('timeout', 'python3 timeout.py', TIMEOUT)]
    resp = codebox.exec_commands(command, ref_dir=tempdir)
    assert resp['timeout']['stdout'] == ''
    assert 'ERROR: Time limit exceeded' in resp['timeout']['stderr']


def test_multiple_commands():
    source = '''#!/bin/bash
exit 1
'''
    sourcetree = {'exit.sh': source}
    tempdir = '/tmp/test_multiple_commands'
    save_sources(sourcetree, tempdir)
    commands = [
        ('1', 'ls -l -h -a /srv', TIMEOUT),
        ('2', 'echo abcd', TIMEOUT),
        ('3', 'bash exit.sh', TIMEOUT),
        ('4', 'echo nothing', TIMEOUT),
    ]
    result = codebox.exec_commands(commands, ref_dir=tempdir)
    assert len(result) == 3


def test_command_not_found():
    commands = [
        ('1', 'ls -l -h -a /srv', TIMEOUT),
        ('2', 'echo abcd', TIMEOUT),
        ('3', 'alksajkjalja', TIMEOUT),
        ('4', 'echo nothing', TIMEOUT),
    ]
    result = codebox.exec_commands(commands)
    assert len(result) == 3
    assert 'Command not found' in result['3']['stderr']


def test_save_path_sep():
    '''
    Verifica se nomes de arquivos que começam com '/' estão sendo devidamente
    tratados
    '''
    sourcetree = {
        '/tmp/lixo.sh': 'echo "lixo"',
    }
    tempdir = '/tmp/test_save_path_sep'
    save_sources(sourcetree, tempdir)
    assert exists('/tmp/test_save_path_sep/tmp/lixo.sh')


def test_run():
    text = 'Test\nRun'
    source = '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
    sourcetree = {
        '__init__.py': '',
        'test.py': source,
        'doc/index.rst': 'Title\n=====\n\nOne paragraph'
    }
    commands = [
        ('bash', 'echo hello wold', 0.1),
        ('python', 'python3 test.py', 0.1),
    ]
    result = codebox.run(sourcetree, commands, input_=text)
    assert 'lint' in result
    assert 'metrics' in result
    assert result['python']['stdout'] == 'Test\nRun'


def test_run_nothing():
    result = codebox.run()
    assert result == {}


def test_run_no_sourcetree():
    result = codebox.run(commands=[('bash', 'echo test', TIMEOUT)])
    assert result['bash']['stdout'] == 'test\n'


def test_no_commands():
    sourcetree = {
        '__init__.py': '',
        'test.py': '#!/usr/bin/python3',
        'doc/index.rst': 'Title\n=====\n\nOne paragraph'
    }
    result = codebox.run(sourcetree)
    assert 'lint' in result and 'test.py' in result['lint']
    assert '__init__.py' in result['metrics']
