#!/usr/bin/env python

import sys
import argparse

import cli.app
import cli.interactive



shell = cli.interactive.InteractiveApp(name='foobar')

from sh import sh
shell.add_command(sh)

from ls import ls
shell.add_command(ls)
shell.add_command(ls, name='notls')

from lsof import lsof
shell.add_command(lsof)

@shell.command(name='gugus')
def foo(app):
    app.stdout.write('running {0}, parent: {1}'.format(app.name, app.parent))
foo.add_param("--long", help="use a long listing format", default=False, action="store_true")
foo.add_param("-a", "--all", help="do not ignore entries starting with .", default=False, action="store_true")


shell.run()
