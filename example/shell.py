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

from lsof import lsof
shell.add_command(lsof)


shell.run()
