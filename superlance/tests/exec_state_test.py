import unittest
import os
import signal
from mock import MagicMock

from superlance.compat import StringIO
from superlance.tests.dummy import DummyRPCServer


class ExecStateTests(unittest.TestCase):
    def _getTargetClass(self):
        from superlance.exec_state import ExecState
        return ExecState

    def _makeOne(self, *args, **kwargs):
        obj = self._getTargetClass()(*args, **kwargs)
        obj.stdin = StringIO()
        obj.stdout = StringIO()
        obj.stderr = StringIO()
        obj.debug = True
        return obj

    def test_no_exec(self):
        rpc = DummyRPCServer()
        exec_state = self._makeOne('ls', "PROCESS_EVENT_FATAL", rpc=rpc)
        exec_state.stdin.write('eventname:NOTFATAL len:0\n')
        exec_state.stdin.seek(0)
        exec_state.call = MagicMock()
        exec_state.runforver(test=True)
        self.assertFalse(exec_state.call.called)

    def test_kill(self):
        rpc = DummyRPCServer()
        exec_state = self._makeOne('ls', "PROCESS_EVENT_FATAL", rpc=rpc)
        exec_state.stdin.write('eventname:PROCESS_EVENT_FATAL len:0\n')
        exec_state.stdin.seek(0)
        exec_state.call = MagicMock()
        exec_state.runforver(test=True)
        self.assertTrue(exec_state.call.called)
