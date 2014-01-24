#!/usr/bin/env python

import sys
import argparse

import cli.app


import os
@cli.app.CommandLineApp(name='sh')
def sh(app):
    """Run the given arguments as a command in the shell.
    """
    print(app.params.command)
    os.system(' '.join(app.params.command))

sh.add_param('command', nargs=argparse.REMAINDER,
        help='the command to pass to the shell.')

if __name__ == '__main__':
    sh.run()
