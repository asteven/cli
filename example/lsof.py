#!/usr/bin/env python

import cli.app

@cli.app.CommandLineApp
def lsof(app):
    app.stdout.write('running %s' % app.name)

lsof.add_param("-a", help="causes list selection options to be ANDed, as described above.", default=False, action="store_true")
lsof.add_param("-b", help="causes lsof to avoid kernel functions that might block - lstat(2), readlink(2), and stat(2).", default=False, action="store_true")

if __name__ == '__main__':
    lsof.run()
