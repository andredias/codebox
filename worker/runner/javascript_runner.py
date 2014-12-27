from .runner import Runner


class JavascriptRunner(Runner):

    sourcefilename = '/tmp/source.js'

    def _run_command(self):
        return ['nodejs', self.sourcefilename]
