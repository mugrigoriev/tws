# Tornado websockets example
# 2016 Mikhail Grigoryev <m.u.grigoriev@gmail.com>

# Test: $ python -m tornado.testing discover

import datetime
import settings
from tornado import ioloop, web, websocket
from tornado.websocket import WebSocketClosedError


class PingHandler(websocket.WebSocketHandler):
    ping_callback = None
    no_pong_callback = None

    def data_received(self, chunk):
        pass  # Empty method for non-production only

    # Empty check for non-production only
    def check_origin(self, origin):
        return True

    def open(self):
        try:
            self.write_message('hello')
            # Starting ping callback:
            self.ping_callback = ioloop.PeriodicCallback(self.send_ping, settings.WS_PING_INTERVAL)
            # Starting pong timeout callback
            self.no_pong_callback = ioloop.PeriodicCallback(self.no_pong_no_love, settings.WS_PONG_TIMEOUT)
            self.ping_callback.start()
            print('Ping started')
        except Exception as e:
            print('Unknown exception: ' + str(e.args))

    def on_message(self, message):
        try:
            self.write_message(message)  # echo
            print(str(message))
        except Exception as e:
            print('Unknown exception: ' + str(e.args))

    def on_close(self):
        try:
            self.stop_ping()
            self.write_message('bye')
        except WebSocketClosedError:
            print('Client disconnected')

    def send_ping(self):
        try:
            if self.stream.closed() and self.ping_callback is not None:
                self.stop_ping()
            else:
                self.ping(b'')
                print(str(datetime.datetime.utcnow()) + ' ping')
                if not self.no_pong_callback.is_running():
                    self.no_pong_callback.start()
                    print('No pong callback started')
        except Exception as e:
            print('Unknown exception: ' + str(e.args))
            self.stop_ping()

    def on_pong(self, data):
        try:
            if self.no_pong_callback.is_running():
                self.no_pong_callback.stop()
                print('No pong callback stopped')
            print(str(datetime.datetime.utcnow()) + ' pong')
        except Exception as e:
            print('Unknown exception: ' + str(e.args))
            #self.stop_ping()

    def no_pong_no_love(self):
        print('no_pong_no_love started')
        self.close()
        print('Connection closed')
        self.no_pong_callback.stop()

    def stop_ping(self):
        self.ping_callback.stop()
        print('Ping stopped')


try:
    app = web.Application([
        (r"/", PingHandler),
    ])
    if __name__ == "__main__":
        app.listen(settings.TORNADO_PORT)
        print('Server address: ws://localhost:' + str(settings.TORNADO_PORT))
        ioloop.IOLoop.current().start()
except KeyboardInterrupt:
    print('Exit')
except Exception as e:
    print('Unknown exception: ' + str(e.args))
