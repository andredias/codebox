from .runner import Runner


class RubyRunner(Runner):

    sourcefilename = '/tmp/source.rb'

    def _run_command(self):
        return ['ruby', self.sourcefilename]
