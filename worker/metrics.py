'''
Several routines to collect metrics for different languages.
The project escomplex provides a nice list of software metrics
that should be obtained in other languages besides javascript.

See: https://github.com/philbooth/escomplex/blob/master/README.md#metrics
'''

import sh
import json

from os.path import splitext


def radon(filename):
    '''
    Collect some software metrics via radon:

        * cyclomatic_complexity
        * loc
        * halstead

    see: https://radon.readthedocs.org/en/latest/
    '''
    from radon.cli import Config
    from radon.cli.harvest import CCHarvester, RawHarvester
    from radon.complexity import SCORE
    from radon.metrics import h_visit

    # ---
    # gambiarra para Radon v1.1.1 ler corretamente arquivos UTF-8
    from contextlib import contextmanager
    import radon.cli.harvest
    import io
    import sys

    @contextmanager
    def _open(path):
        if path == '-':
            yield sys.stdin
        else:
            with io.open(path, encoding='utf-8') as f:
                yield f

    radon.cli.harvest._open = _open
    # fim da gambiarra
    # ---

    config = Config(average=True, exclude=None, ignore=None, max='F', min='A', no_assert=True,
                    order=SCORE, show_closures=True, show_complexity=True,
                    total_average=False)
    path = [filename]
    metrics = {}
    metrics['cyclomatic_complexity'] = CCHarvester(path, config)._to_dicts()
    config = Config(exclude=None, ignore=None, summary=False)
    metrics['loc'] = dict(RawHarvester(path, config).results)
    with open(filename, encoding='utf-8') as f:
        try:
            metrics['halstead'] = h_visit(f.read())._asdict()
        except SyntaxError:
            pass
    return metrics


def complexity_report(filename):
    '''
    Javascript
    complexity-report (https://github.com/philbooth/complexity-report)
    '''
    report = json.loads(str(sh.cr('-t', '-f', 'json', filename)))
    metrics = {}
    sloc = report['reports'][0]['aggregate']['sloc']
    metrics['loc'] = {
        'sloc': sloc['logical'],
        'loc': sloc['physical']
    }
    metrics['hastead'] = report['reports'][0]['aggregate']['halstead']
    return metrics


func = {
    '.py': radon,
    '.js': complexity_report,
}


def collect_metrics(filename):
    extension = splitext(filename)[1]
    return func.get(extension, lambda x: {})(filename)
