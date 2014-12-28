import os
import sh

TIMEOUT_EXIT_CODE = 124


class Runner(object):

    '''
    Generic class to manage source code processing
    '''

    sourcefilename = '/tmp/sourcefile'
    execfilename = '/tmp/a.out'
    _timeout = 5
    ok_code = list(range(128))  # sh does not work with python3 range yet

    def __call__(self, job):
        if not job['source']:
            return {}
        self.job = job
        self.response = {}
        self.input = job.get('input', None)
        self.timeout = job.get('timeout', self._timeout)
        # save source to a temporary file for compiling and running it later
        with open(self.sourcefilename, mode='w', encoding='utf-8') as sourcefile:
            sourcefile.write(job['source'])
        self.evaluate()
        self.compile() and self.run()
        return self.response

    def evaluate(self):
        pass

    def compile(self):
        command = self._compile_command()
        if command is None:
            return True
        output = command('-o', self.execfilename, self.sourcefilename, _ok_code=self.ok_code)
        self.response['compilation'] = {
            'stdout': output.stdout.decode('utf-8'),
            'stderr': output.stderr.decode('utf-8'),
            'exit_code': output.exit_code,
        }
        return output.exit_code == 0

    def _compile_command(self):
        return None

    def run(self):
        os.setresuid(1000, 1000, 0)  # run as 'user'
        try:
            output = sh.timeout('--foreground', self.timeout, *self._run_command(), _in=self.input,
                                _ok_code=self.ok_code)
        finally:
            os.setresuid(0, 0, 0)  # back to 'root'
        timeout_msg = ''
        if output.exit_code == TIMEOUT_EXIT_CODE:
            timeout_msg = '\nERROR: Running time limit exceeded %ss' % self.timeout
        self.response['execution'] = {
            'stdout': output.stdout.decode('utf-8'),
            'stderr': output.stderr.decode('utf-8') + timeout_msg,
            'exit_code': output.exit_code,
        }
        return

    def _run_command(self):
        return [self.execfilename]
