#!/usr/bin/env python

import sys
import logging
import argparse
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s', stream=sys.stderr)

import cli.app
import cli.log
import cli.interactive

from cli import param, command

cli.default_app_class = cli.app.CommandLineApp
#cli.default_app_class = cli.log.LoggingApp


@param("-a", "--all", help="do not ignore entries starting with .", default=False, action="store_true")
@command
def command_with_one_param(app):
    app.stdout.write('running {0}, {1} with: {2}\n'.format(app, app.name, app.params))
command_with_one_param.run(exit_after=False)

@param("--long", help="use a long listing format", default=False, action="store_true")
@param("-a", "--all", help="do not ignore entries starting with .", default=False, action="store_true")
@command
def command_with_params(app):
    app.stdout.write('running {0}, {1} with: {2}\n'.format(app, app.name, app.params))
command_with_params.run(exit_after=False)

@param("--long", help="use a long listing format", default=False, action="store_true")
@param("-a", "--all", help="do not ignore entries starting with .", default=False, action="store_true")
def only_param(app):
    app.stdout.write('running {0}, {1} with: {2}\n'.format(app, app.name, app.params))

only_param.run(exit_after=False)

@command
def only_command(app):
    app.stdout.write('running {0}, {1} with: {2}\n'.format(app, app.name, app.params))
only_command.run(exit_after=False)


@command(app_class=cli.log.LoggingApp)
def only_command_logging(app):
    app.stdout.write('running {0}, {1} with: {2}\n'.format(app, app.name, app.params))
only_command_logging.run(exit_after=False)

@param("--long", help="use a long listing format", default=False, action="store_true")
@param("-a", "--all", help="do not ignore entries starting with .", default=False, action="store_true")
@command(app_class=cli.log.LoggingApp)
def command_logging_with_params(app):
    app.stdout.write('running {0}, {1} with: {2}\n'.format(app, app.name, app.params))
command_logging_with_params.run(exit_after=False)
