from genericpath import exists
import os
import sys
import json
import shlex
from pathlib import Path
from subprocess import call, check_output, Popen, PIPE, TimeoutExpired
from tempfile import TemporaryDirectory
from .metrics.lint import lint
from .metrics.metrics import collect_metrics
from .models import Sourcefiles


def save_sources(dest_dir: Path, sources: Sourcefiles) -> None:
    '''
    Save sources to a temporary directory
    '''
    for path, code in sources.items():
        p = dest_dir / path.lstrip(os.sep)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(code)
    return


def run_project(sources: Sourcefiles, commands=None, input_=None):
    '''
    commands = [(phase, line, timeout), ...]
    '''
    input_ = input_ or ''
    response = {}
    with TemporaryDirectory() as tempdir:
        os.chdir(tempdir)
        dest_dir = Path(tempdir)
        save_sources(dest_dir, sources)


        if sourcetree:
            save_sourcetree(sourcetree)
            response.update(evaluate(sourcetree.keys()))
        # não executar nenhum comando como root
        ruid, euid, suid = os.getresuid()
        is_root = ruid == 0
        if is_root:
            os.system('chown -R 1000:1000 %s' % tempdir)
            os.setresuid(1000, 1000, 0)  # run as 'user'
        try:
            response.update(exec_commands(commands, input_))
        finally:
            if is_root:
                os.setresuid(ruid, euid, suid)  # back to 'root'
    return response



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
