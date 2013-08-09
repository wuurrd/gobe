from tulip.http.server import ServerHttpProtocol
from tulip.http import Response, Session, request
from tulip import get_event_loop
from tulip import task
import traceback
import signal


class HttpServer(ServerHttpProtocol):
    def __init__(self, *args, **kwargs):
        self.session = Session()
        super().__init__(*args, **kwargs)

    @task
    def handle_request(self, message, payload):
        """Handle a single http request.

        Subclass should override this method. By default it always
        returns 404 response.

        info: tulip.http.RequestLine instance
        message: tulip.http.RawHttpMessage instance
        """
        url = message.path
        method = message.method
        print(url)
        try:
            received_response = yield from request(
                'get', url, session=self.session)
        except Exception as e:
            forwarded_response = Response(self.transport,
                                          500,
                                          http_version=message.version,
                                          close=True)
            body = bytes(repr(e),
                         encoding='utf-8',
                         errors='ignore')
        else:
            forwarded_response = Response(self.transport,
                                          received_response.status,
                                          http_version=message.version,
                                          close=True)
            body = yield from received_response.read()
            body = bytes(body)

            for header, value in received_response.items():
                forwarded_response.add_headers((header, value))
        forwarded_response.send_headers()
        forwarded_response.write(body)
        forwarded_response.write_eof()
        self.keep_alive(False)


def main():
    loop = get_event_loop()
    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
    except RuntimeError:
        pass

    task = loop.start_serving(
        lambda: HttpServer(debug=True, keep_alive=75), '0.0.0.0', 8080)
    socks = loop.run_until_complete(task)
    print('serving on', socks[0].getsockname())
    loop.run_forever()

if __name__ == '__main__':
    main()
