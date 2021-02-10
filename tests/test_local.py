from os.path import exists
from pathlib import Path

from pytest import mark

from app.codebox import execute, save_sources  # isort:skip
from app.models import Command, Response  # isort:skip

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


@mark.parametrize("command,response", [
    (
        Command(type='bash', command='echo 1 2 3', timeout=TIMEOUT),
        Response(stdout='1 2 3\n', stderr='', exit_code=0)
    ),
    (
        Command(type='bash', command='python -c "print(1, 2, 3)"', timeout=TIMEOUT),
        Response(stdout='1 2 3\n', stderr='', exit_code=0)
    ),
    (
        Command(type='bash', command=f'sleep {TIMEOUT + 0.05}', timeout=TIMEOUT),
        Response(stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1)
    ),
    (
        Command(type='bash', command='', timeout=TIMEOUT),
        Response(stdout='', stderr='', exit_code=0)
    ),
    (
        Command(type='bash', command='nao_existe 1 2 3', timeout=TIMEOUT),
        Response(stdout='', stderr='/bin/sh: 1: nao_existe: Permission denied\n', exit_code=127)
    ),
    (
        Command(type='bash', command='rm -rf /home', timeout=TIMEOUT),
        Response(stdout='', stderr="rm: cannot remove '/home': Permission denied\n", exit_code=1)
    )
])
def test_execute(command, response):
    result = execute(command)
    assert response == result


@mark.skip
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


@mark.skip
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


@mark.skip
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


@mark.skip
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


@mark.skip
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


@mark.skip
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


@mark.skip
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


@mark.skip
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


@mark.skip
def test_run_nothing():
    result = codebox.run()
    assert result == {}


@mark.skip
def test_run_no_sourcetree():
    result = codebox.run(commands=[('bash', 'echo test', TIMEOUT)])
    assert result['bash']['stdout'] == 'test\n'


@mark.skip
def test_no_commands():
    sourcetree = {
        '__init__.py': '',
        'test.py': '#!/usr/bin/python3',
        'doc/index.rst': 'Title\n=====\n\nOne paragraph'
    }
    result = codebox.run(sourcetree)
    assert 'lint' in result and 'test.py' in result['lint']
    assert '__init__.py' in result['metrics']
