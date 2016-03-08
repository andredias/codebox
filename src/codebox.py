#!/usr/bin/python3

import os
import shutil
import sys
import json
import shlex
from subprocess import call, check_output, Popen, PIPE, TimeoutExpired
from tempfile import mkdtemp
from metrics.lint import lint
from metrics.metrics import collect_metrics

TIMEOUT_EXIT_CODE = 124


def run(sourcetree=None, commands=None, input_=None):
    '''
    commands = [(phase, line, timeout), ...]
    '''
    input_ = input_ or ''
    sourcetree = sourcetree or {}
    commands = commands or []
    response = {}
    ruid, euid, suid = os.getresuid()
    is_root = ruid == 0
    if is_root:
        os.setresuid(1000, 1000, 0)  # run as 'user'
    try:
        tempdir = mkdtemp()
        os.chdir(tempdir)
        if sourcetree:
            save_sourcetree(sourcetree)
            response.update(evaluate(sourcetree.keys()))
        response.update(exec_commands(commands, input_))
        shutil.rmtree(tempdir)
    finally:
        if is_root:
            os.setresuid(ruid, euid, suid)  # back to 'root'
    return response


def save_sourcetree(sourcetree, destdir=''):
    '''
    Save sources to a temporary directory
    '''
    for name, source in sourcetree.items():
        filename = os.path.join(destdir, name.lstrip(os.path.sep))
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filename, mode='w', encoding='utf-8') as f:
            f.write(source)


def evaluate(filenames, ref_dir=''):
    result = {}
    result['lint'] = {}
    result['metrics'] = {}
    for filename in filenames:
        tempfilename = os.path.join(ref_dir, filename)
        lint_result = lint(tempfilename)
        if lint_result:
            result['lint'][filename] = lint_result
        metrics_result = collect_metrics(tempfilename)
        if metrics_result:
            result['metrics'][filename] = metrics_result
    return result


def exec_commands(commands, input_=None, ref_dir=''):
    if ref_dir:
        os.chdir(ref_dir)
    response = {}
    exit_code = 0
    for phase, command, timeout in commands:
        # TODO: substituir por run quando chegar o Python 3.5
        # trecho abaixo baseado no exemplo de:
        # https://docs.python.org/3/library/subprocess.html#subprocess.Popen.communicate
        if isinstance(command, str):
            command = shlex.split(command)
        try:
            proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            output, errors = proc.communicate(input=input_, timeout=timeout)
            exit_code = proc.returncode
        except FileNotFoundError:
            output = ''
            errors += '\nCommand not found'
            exit_code = -1
        except TimeoutExpired:
            # remove todos os processos filhos e descendentes
            pid = os.getpid()
            # todos menos o primeiro da lista devem ser mortos
            children = check_output(['pgrep', '-g', str(pid)]).decode('utf-8').splitlines()[1::]
            children = children[::-1]
            for child in children:
                call(['kill', '-TERM', child])
            output, errors = proc.communicate()  # segunda chance de terminar por bem
            exit_code = proc.returncode or 1
            errors += '\nERROR: Time limit exceeded %ss' % timeout

        response[phase] = {
            'stdout': output,
            'stderr': errors,
            'exit_code': exit_code,
        }
        if exit_code != 0:
            break
    return response


if __name__ == '__main__':
    linhas = ''.join(sys.stdin.readlines())
    job = json.loads(linhas)
    response = run(job.get('sourcetree'), job.get('commands'), job.get('input'))
    json.dump(response, sys.stdout)
    sys.exit(0)
