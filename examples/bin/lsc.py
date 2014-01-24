#!/usr/bin/env python

import logging
log = logging.getLogger(__name__)

import cli.app
import cli.log
import cli.complete



class MyApp(cli.complete.CompletionMixin, cli.log.LoggingApp):
    def setup(self):
        cli.log.LoggingApp.setup(self)
        cli.complete.CompletionMixin.setup(self)
        log.debug('MyApp.setup')


@MyApp
def lsc(app):
    app.stdout.write('running %s' % app.name)

lsc.add_param("--long", help="use a long listing format", default=False, action="store_true")
lsc.add_param("-a", "--all", help="do not ignore entries starting with .", default=False, action="store_true")

if __name__ == '__main__':
    lsc.run()
