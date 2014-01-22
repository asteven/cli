"""\
:mod:`cli.interactive` -- interactive applications
--------------------------------------------------

Run a command as an interactive shell. Dispatches user inputs to other 
registered applications.
"""

__license__ = """Copyright (c) 2012 Steven Armstrong <steven-cli@armstrong.cc>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""

import shlex
import argparse
import logging
log = logging.getLogger(__name__)

from cli.app import CommandLineApp, CommandLineMixin, Application, Abort
from cli.log import LoggingMixin
from cli.complete import CommandCompleter

__all__ = ['InteractiveApp', 'InteractiveMixin', 'InteractiveAppCompleter']


class InteractiveAppCompleter(CommandCompleter):
    """A special form of command completer that completes on command names
    and then delegates the completion of command arguments to a command
    specific completer.
    """
    def __init__(self, commands, logger=None):
        self.commands = commands
        self.log = logger or logging.getLogger(self.__class__.__name__)
        self.current_candidates = []

    def complete(self, first, current, previous, words, index):
        self.log.debug('complete: first=%s, current=%s, previous=%s, words=%s, index=%s',
            first, current, previous, words, index)
        current_candidates = []
        if index == 0:
            candidates = sorted(self.commands.keys())
            if current:
                # match options with portion of input being completed
                current_candidates = [w for w in candidates
                                            if w.startswith(current)]
            else:
                # matching empty string so use all candidates
                current_candidates = candidates
        else:
            # delegate to commands own completer
            command = self.commands[first]
            if not hasattr(command, 'completer'):
                command.completer = CommandCompleter(command.actions)
            current_candidates = command.completer.complete(first, current, previous, words, index)
        return current_candidates


class InteractiveMixin(object):
    """A shell like command-line application that takes inputs from a user
    and dispatches them to other registered applications.
    """
    def __init__(self, prompt=None, readline_history=False, readline_completekey='tab', **kwargs):
        self.stop = False
        self.prompt = prompt
        self.readline_history = readline_history
        self.readline_completekey = readline_completekey
        self.commands = {}

    def setup(self):
        """Configure the :class:`InteractiveMixin`.

        This method adds the :option:`-i` parameter to the application.
        """
        if not self.prompt:
            self.prompt = '%s> ' % self.name
        self.add_param('-i', '--interactive', default=False, action='store_true',
                help='run the application interactively as a shell')
        self.add_param('remainder', nargs=argparse.REMAINDER,
                help='the remaining arguments are treated as input to the shell')

    def pre_run(self):
        self.log.debug('pre_run')
        if self.readline_history:
            self.configure_readline_history()
        if self.readline_completekey:
            self.configure_readline_completer()

    def command(self, main=None, name=None, **kwargs):
        app = CommandLineApp(main=main, **kwargs)
        app.parent = self
        self.add_command(app, name=name)
        return app

    def add_command(self, command, name=None):
        command_name = name or command.name
        command.parent = self
        self.commands[command_name] = command

    def configure_readline_history(self):
        try:
            # Configure readline history
            import readline
            if hasattr(readline, 'read_history_file'):
                # Don't clutter the users home directory
                config_home = os.environ.get('XDG_CONFIG_HOME', '~/.config')
                history_file = os.path.join(config_home, '%s.history' % self.name)
                self.log.debug('Using readline history file: %s', history_file)

                def save_history(history_file):
                    readline.write_history_file(history_file)

                import atexit
                atexit.register(save_history, history_file)

                if os.path.isfile(history_file):
                    readline.read_history_file(history_file)

        except ImportError:
            self.log.warn('Failed to import module: readline')
        except IOError, e:
            self.log.warning(e)

    def configure_readline_completer(self):
        try:
            import readline
            self.old_completer = readline.get_completer()
            self.completer = InteractiveAppCompleter(self.commands, logger=self.log)
            readline.set_completer(self.completer.complete_readline)
            orig_completer_delims = readline.get_completer_delims()
            # remove - (dash) from completer delims as we also want to complete command line arguments
            completer_delims = orig_completer_delims.replace('-', '')
            self.log.debug('Setting completer_delims to {}'.format(completer_delims))
            readline.set_completer_delims(completer_delims)

            readline.parse_and_bind(self.readline_completekey +': complete')
        except ImportError:
            self.log.warn('Failed to import module: readline')

    def readline(self):
        prompt = ''
        if self.stdin.isatty() and self.params.interactive:
            prompt = self.prompt
        return raw_input(prompt)

    def input_loop(self):
        if self.stdin.isatty() and not self.params.interactive:
            # remaining command line args if any
            if self.params.remainder:
                if self.params.remainder[0] == '--':
                    remainder = self.params.remainder[1:]
                else:
                    remainder = self.params.remainder
                line = ' '.join(remainder)
                yield line
            return
        try:
            # line by line from stdin
            while True:
                line = self.readline()
                yield line
        except EnvironmentError as e:
            raise cli.app.Error('Failed to read from stdin: %s' % e)
        except EOFError as e:
            pass

    def interact(self):
        # FIXME: split interpreter from console, @see ~/vcs/icos/sandbox/python/console.py
        for line in self.input_loop():
            if line:
                argv = shlex.split(line)
                self.log.debug('line: %s', line)
                self.log.debug('argv: %s', argv)
                if line == 'quit':
                    break
                if line == 'commands':
                    self.stdout.write('\n'.join(self.commands.keys()))
                elif argv[0] in self.commands:
                    try:
                        #self.commands[argv[0]].argv = argv
                        #self.commands[argv[0]].exit_after_main = False
                        self.commands[argv[0]].run(argv=argv, exit_after=False)
                    except Abort as e:
                        pass
                else:
                    self.stdout.write('You said: %s\n' % line)
                self.stdout.write('\n')
                self.stdout.flush()


class InteractiveApp(
    InteractiveMixin, LoggingMixin, CommandLineMixin, Application):
    """An interactive application.

    This class simply glues together the base :class:`Application`,
    :class:`InteractiveMixin` and other mixins that provide necessary
    functionality.
    """

    def __init__(self, main=None, **kwargs):
        InteractiveMixin.__init__(self, **kwargs)
        LoggingMixin.__init__(self, **kwargs)
        CommandLineMixin.__init__(self, **kwargs)
        Application.__init__(self, main, **kwargs)

    def setup(self):
        Application.setup(self)
        CommandLineMixin.setup(self)
        LoggingMixin.setup(self)
        InteractiveMixin.setup(self)
        self.log.debug('InteractiveApp.setup')

    def pre_run(self):
        self.log.debug('InteractiveApp.pre_run')
        Application.pre_run(self)
        CommandLineMixin.pre_run(self)
        LoggingMixin.pre_run(self)
        InteractiveMixin.pre_run(self)

    def main(self):
        self.interact()
