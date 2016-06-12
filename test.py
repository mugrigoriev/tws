# coding=utf-8
'''
Application to demonstrate testing tornado websockets.

Try it wiith: python -m tornado.testing discover
'''


from tornado import testing, httpserver, gen, websocket
from tornado.ioloop import TimeoutError
import settings
from tws import app as APP
import time


class TestChatHandler(testing.AsyncTestCase):

    def setUp(self):
        super(TestChatHandler, self).setUp()
        server = httpserver.HTTPServer(APP)
        socket, self.port = testing.bind_unused_port()
        server.add_socket(socket)

    def _mk_connection(self):
        return websocket.websocket_connect(
            'ws://localhost:{}/'.format(self.port)
        )

    @gen.coroutine
    def _mk_client(self):
        c = yield self._mk_connection()

        # Discard the hello
        # This could be any initial handshake, which needs to be generalized
        # for most of the tests.
        _ = yield c.read_message()

        raise gen.Return(c)

    @testing.gen_test
    def test_hello(self):
        c = yield self._mk_connection()
        # Get the initial hello from the server.
        response = yield c.read_message()
        # Make sure that we got a 'hello' not 'bye'
        self.assertEqual('hello', response)

    @testing.gen_test
    def test_echo(self):
        # A client with the hello taken care of.
        c = yield self._mk_client()

        # Send a 'foo' to the server.
        c.write_message("foo")
        # Get the 'foo' back.
        response = yield c.read_message()
        # Make sure that we got a 'foo' back and not 'bar'.
        self.assertEqual('foo', response)

    # Попытка протестировать пинг. На самом деле, автоматический пинг-понг реализован в WebSocketClientConnection.
    '''
    @testing.gen_test
    def test_ping(self):
        c = yield self._mk_client()
        msg = None
        try:
            while True:
                msg = yield c.read_message()
                if msg is None:
                    break
                # TODO Do something with msg
            self.assertEqual(None, msg)
        except TimeoutError:
            self.assertEqual(None, msg)
    '''
