#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import subprocess

from supervisor import childutils
from superlance.process_state_monitor import ProcessStateMonitor

# A supervisor config snippet that performs suicide.
#
# [eventlistener:suicide]
# command=exec_state -d -c '/usr/bin/supervisorctl shutdown' -s PROCESS_STATE_FATAL
# events=PROCESS_STATE
#

doc = """\
exec_state.py -c <command> [-s state]

Options:

-c -- Command to execute

-s -- Process state. Default PROCESS_STATE_FATAL.
"""


class ExecState(object):
    def __init__(self, command, state, rpc=None):
        self.command = command
        self.state = state
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.rpc = rpc
        self.debug = False
        self.call = subprocess.call

    def runforver(self, test=False):
        while True:
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)
            if self.debug:
                print("received: ", headers, payload, file=self.stderr)
            if headers['eventname'] != self.state:
                print("events did not match: ", headers['eventname'], self.state, file=self.stderr)
                childutils.listener.ok(self.stdout)
                if test:
                    break
                continue

            ret = self.call(self.command, shell=True)

            if test:
                break
            childutils.listener.ok(self.stdout)


def usage():
    print(doc)
    sys.exit(255)


def exec_from_args(arguments):
    import getopt
    short_args = "hc:s:d"
    long_args = [
        "help",
        "command",
        "state",
        "debug",
    ]

    if not arguments:
        return None

    arg_state = 'PROCESS_STATE_FATAL'
    arg_debug = False

    try:
        opts, args = getopt.getopt(arguments, short_args, long_args)
    except Exception:
        return None

    for option, value in opts:
        if option in ('-h', '--help'):
            return None
        if option in ('-c', '--command'):
            arg_command = value
        if option in ('-s', '--state'):
            arg_state = value
        if option in ('-d', '--debug'):
            arg_debug = True

    exec_state = ExecState(arg_command, arg_state)
    exec_state.debug = arg_debug
    return exec_state


def main():
    exec_state = exec_from_args(sys.argv[1:])
    if exec_state is None:
        usage()

    exec_state.rpc = childutils.getRPCInterface(os.environ)
    exec_state.runforver()


if __name__ == "__main__":
    main()
