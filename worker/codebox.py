#!/usr/bin/python3

import io
import os
import re
import sh
import shutil
import sys
import json
from tempfile import mkdtemp
from .lint import lint
from .metrics import collect_metrics

TIMEOUT_EXIT_CODE = 124


def run(sourcetree=None, commands=None, input_=None):
    '''
    commands = [(phase, line, timeout), ...]
    '''
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
    ok_code = range(128)
    exit_code = 0
    for phase, command, timeout in commands:
        command, *args = re.sub(r'\s+', ' ', command).split()  # *args não funciona no python2
        command = sh.Command(command)
        timeout_msg = ''
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            output = command(*args, _in=input_, _timeout=timeout, _encoding='utf-8',
                             _ok_code=ok_code, _out=stdout, _err=stderr)
            exit_code = output.exit_code
        except sh.TimeoutException:
            timeout_msg = '\nERROR: Time limit exceeded %ss' % timeout
        response[phase] = {
            'stdout': stdout.getvalue(),
            'stderr': stderr.getvalue() + timeout_msg,
            'exit_code': exit_code,
        }
        if exit_code != 0:
            break
    return response


if __name__ == '__main__':
    linhas = ''.join(sys.stdin.readlines())
    job = json.loads(linhas)
    response = run(job)
    json.dump(response, sys.stdout)
    sys.exit(0)
