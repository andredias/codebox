import json

from subprocess import run


def execute(sourcetree=None, commands=None, input_=''):
    sourcetree = sourcetree or {}
    commands = commands or []
    job = {
        'input': input_,
        'sourcetree': sourcetree,
        'commands': commands
    }
    job_json = json.dumps(job)
    # Rodar com versão local do código fonte
    # print(job_json)
    # output = run_command('docker run -i --rm -v {0}:/{1}_1:ro --workdir /{1}_1 {1}'.format(CODEBOX_SOURCE_DIR, IMAGE),
    #                      input=job_json)
    output = execute('docker run -i --rm {}'.format(IMAGE), input=job_json)
    return json.loads(output)


FILENAME = 'main.py'
TIMEOUT = 0.1
COMMAND = dict(command='python main.py', timeout=TIMEOUT)


def mount_input(code: str, input: str = '') -> None:
    pass


def test_hello_world():
    '''
    Program supposed to run smoothly. But no input needed
    '''
    source = 'print("Hello, World!")'
    resp = execute(source)
    assert resp['execution']['stdout'].strip() == 'Hello, World!'
    assert resp['execution']['stderr'] == ''


def test_program_error():
    '''
    Python program with a syntax error
    '''
    source = '''import os

sys.stdout.write('Olá mundo!')'''
    resp = execute(source)
    assert resp['execution']['stdout'] == ''
    assert "NameError: name 'sys' is not defined" in resp['execution']['stderr']


def test_empty():
    '''
    Running a empty source
    '''
    resp = execute()
    assert resp == {}


def test_input():
    text = 'Hello\nWorld'
    source = '''import sys

for line in sys.stdin.readlines():
sys.stdout.write(line)
'''
    resp = execute(source, text)
    assert resp['execution']['stdout'] == 'Hello\nWorld'
    assert resp['execution']['stderr'] == ''
    assert resp['lint'] == {}


def test_utf_8_input():
    text = 'Olá\nAçúcar'
    source = '''import sys

for line in sys.stdin.readlines():
sys.stdout.write(line)
'''
    resp = execute(source, text)
    assert resp['execution']['stdout'] == 'Olá\nAçúcar'
    assert resp['execution']['stderr'] == ''
    assert resp['lint'] == {}


def test_timeout():
    source = 'import time\nprint("Going to sleep...")\ntime.sleep(5)\nprint("Overslept!")'
    resp = execute(source)
    assert resp['execution']['stdout'] == ''
    assert 'ERROR: Time limit exceeded' in resp['execution']['stderr']


def test_net_access():
    source = 'from subprocess import check_output\n\nprint(check_output(["ping", "-c", "1", "www.google.com"]))'
    resp = execute(source)
    assert resp['execution']['stderr'] == ''
    assert 'PING www.google.com (' in resp['execution']['stdout']


def test_evaluation():
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
    resp = execute(source)
    assert resp['execution']['stderr'] == ''
    assert 'source.py' in resp['lint']
    assert 'source.py' in resp['metrics']
    assert len(resp['lint']['source.py']) > 0
    assert isinstance(resp['metrics']['source.py']['cyclomatic_complexity'], list)
    assert len(resp['metrics']['source.py']['cyclomatic_complexity']) > 3
    assert 'source.py' not in resp['metrics']['source.py']['loc']


def test_syntax_error():
    source = '''import sys
def outer(x):
    def inner():
        print x
    return inner
'''
    resp = execute(source)
    assert 'IndentationError: unexpected indent' in resp['execution']['stderr']
    assert 'source.py' in resp['lint']
    assert 'source.py' in resp['metrics']


def test_access_to_worker_dir():
    source = 'from subprocess import check_output\n\nprint(check_output(["ls", "-R", "/%s"]))' % IMAGE
    resp = execute(source)
    assert ('cannot open directory /%s: Permission denied' % IMAGE) in resp['execution']['stderr']


def test_utf_8():
    source = 'print("Olá, açúcar, lâmpada")'
    resp = execute(source)
    assert resp['execution']['stdout'] == 'Olá, açúcar, lâmpada\n'
    assert resp['execution']['stderr'] == ''
