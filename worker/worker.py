#!/usr/bin/python3

import sys
import json
from runner import CRunner, CPPRunner, GoRunner, JavascriptRunner, PythonRunner, RubyRunner

languages = {
    'c': CRunner,
    'cpp': CPPRunner,
    'c++': CPPRunner,
    'go': GoRunner,
    'javascript': JavascriptRunner,
    'python': PythonRunner,
    'ruby': RubyRunner,
}


if __name__ == '__main__':
    linhas = ''.join(sys.stdin.readlines())
    entrada = json.loads(linhas)
    if entrada['language'] not in languages:
        sys.exit('There is no Runner class for %s' % entrada['language'])
    runner = languages[entrada['language'].lower()]()
    response = runner(entrada)
    json.dump(response, sys.stdout)
    sys.exit(0)
