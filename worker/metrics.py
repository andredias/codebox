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
    from radon.metrics import h_visit

    config = Config(average=True, exclude=None, ignore=None, max='F', min='A', no_assert=True,
                    order='SCORE', show_closures=True, show_complexity=True,
                    total_average=False)
    path = [filename]
    metrics = {}
    cyclomatic_complexity = CCHarvester(path, config)._to_dicts()
    if cyclomatic_complexity and 'error' not in cyclomatic_complexity[filename]:
        metrics['cyclomatic_complexity'] = cyclomatic_complexity
    config = Config(exclude=None, ignore=None, summary=False)
    metrics['loc'] = dict(RawHarvester(path, config).results)
    with open(filename, encoding='utf-8') as f:
        try:
            metrics['halstead'] = h_visit(f.read())._asdict()
        except SyntaxError:
            pass
    return metrics


func = {
    '.py': radon,
}


def collect_metrics(filename):
    extension = splitext(filename)[1]
    return func.get(extension, lambda x: {})(filename)
