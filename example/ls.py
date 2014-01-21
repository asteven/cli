#!/usr/bin/env python

import cli.app
import cli.log

@cli.app.CommandLineApp
def ls(app):
    app.stdout.write('running %s' % app.name)

ls.add_param("-l", help="use a long listing format", default=False, action="store_true")
ls.add_param("-a", "--all", help="do not ignore entries starting with .", default=False, action="store_true")

if __name__ == '__main__':
    ls.run()
