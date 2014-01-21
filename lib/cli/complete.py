"""\
:mod:`cli.complete` -- command completion
-----------------------------------------

Generate shell completions for an application.
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

import os
import sys
import logging
#logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s', stream=sys.stderr)
log = logging.getLogger(__name__)

from cli.app import Application, Abort
from cli.log import LoggingMixin

__all__ = ['CompletionMixin', 'CommandCompleter']


class CommandCompleter(object):
    """Readline and bash command completion.
    """
    def __init__(self, actions, exclude=None):
        self.actions = actions
        self.current_candidates = []

    def _find_action_by_option_string(self, option_string):
        for action in self.actions.values():
            if option_string in action.option_strings:
                return action
        return None

    def complete(self, first, current, previous, words, index):
        log.debug('complete: first=%s, current=%s, previous=%s, words=%s, index=%s',
            first, current, previous, words, index)
        candidates = []
        try:
            if current:
                existing_options = set(words[:-1])
            else:
                existing_options = set(words)
            log.debug('existing_options: {}'.format(existing_options))
            possible_options = []
            previous_action = self._find_action_by_option_string(previous)
            log.debug('previous_action: {}'.format(previous_action))
            if previous_action and previous_action.nargs != 0:
                # previous action takes an argument, so don't propose any
                # other completions until we have that
                if current:
                    possible_options.append(current)
            else:
                for action in self.actions.values():
                    if existing_options.isdisjoint(set(action.option_strings)):
                        possible_options.extend(action.option_strings)

            if current:
                # match options with portion of input being completed
                candidates = [w for w in possible_options
                                            if w.startswith(current)]
            else:
                # matching empty string so use all candidates
                candidates = possible_options

            log.debug('candidates=%s', candidates)
        except (KeyError, IndexError) as err:
            self.log.debug('completion error: %s', err)
            candidates = []
        return candidates

    # TODO: also implement bash/zsh/shell completion
    #   @see http://www.gnu.org/software/bash/manual/bashref.html#Programmable-Completion
    #   @see /home/sar/vcs/plugit for inspiration
    def complete_bash(self):
        first = sys.argv[1]
        current = sys.argv[2]
        previous = sys.argv[3]
        line = os.environ['COMP_LINE']
        index = os.environ['COMP_POINT']
        words = line.split()
        candidates = self.complete(first, current, previous, words, index)
        log.debug('complete_bash: %s', candidates)
        print '\n'.join(candidates)

    def complete_readline(self, text, state):
        log.debug('complete_readline: text:%s, state:%s', text, state)
        response = None
        if state == 0:
            # This is the first time we are called for this text, so build a match list.
            import readline
            line = readline.get_line_buffer()
            words = line.split()
            index = readline.get_begidx()
            current = text
            first = ''
            if len(words) > 0:
                first = words[0]
            try:
                if len(current) == 0:
                    previous = words[-1]
                else:
                    previous = words[-2]
            except IndexError:
                previous = ''
            self.current_candidates = self.complete(first, current, previous, words, index)
        try:
            response = self.current_candidates[state]
            if len(self.current_candidates) == 1:
                # Add space if there is only one candidate
                response = '{} '.format(response)
        except IndexError:
            response = None
        log.debug('complete_readline(%s, %s) => %s', repr(text), state, response)
        return response


class CompletionMixin(object):
    __arguments = (
        (('--bash-complete',), {'default': False, 'action': 'store_true',
            'help': 'output command completion for use with bashs complete builtin'}),
        (('--bash-eval',), {'default': False, 'action': 'store_true',
            'help': 'print a string to stdout which can be eval\'ed to enable command completion for the current shell'})
    )

    def setup(self):
        """Configure the :class:`CompletionMixin`.

        This method adds the parameters :option:`--bash-complete` and
        :option:`--bash-eval` to the application.
        """
        for (args,kwargs) in self.__arguments:
            self.add_param(*args, **kwargs)

    def run(self):
        """Overload Application.run to handle bash completion calls.
        """
        log.debug('{}.run'.format(self.__class__.__name__))
        parser = self.argparser_factory(
            add_help=False,
            argv=self.argv,
            stdout=self.stdout,
            stderr=self.stderr,
            )
        for (args,kwargs) in self.__arguments:
            parser.add_argument(*args, **kwargs)
        args, rest = parser.parse_known_args(self.argv[1:])
        if args.bash_eval:
            print("complete -C \"{} --bash-complete\" {}".format(self.argv[0], self.argv[0]))
            sys.exit(0)
        elif args.bash_complete:
            log.debug('self.argv: {}'.format(self.argv))
            first = self.argv[2]
            current = self.argv[3]
            previous = self.argv[4]
            line = os.environ['COMP_LINE']
            index = os.environ['COMP_POINT']
            words = line.split()
            # exclude bash completion related actions from completion
            actions = dict([(name,action) for name,action in self.actions.items() if name not in ('bash_complete', 'bash_eval')])
            completer = CommandCompleter(actions)
            candidates = completer.complete(first, current, previous, words, index)
            log.debug('CompletionMixin candidates: %s', candidates)
            print '\n'.join(candidates)
            sys.exit(0)
        else:
            Application.run(self)

