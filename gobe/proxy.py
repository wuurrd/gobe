from tulip.http.server import ServerHttpProtocol
from tulip.http import Response
from tulip import get_event_loop
import signal


class HttpServer(ServerHttpProtocol):
    def handle_request(self, message, payload):
        """Handle a single http request.

        Subclass should override this method. By default it always
        returns 404 response.

        info: tulip.http.RequestLine instance
        message: tulip.http.RawHttpMessage instance
        """
        response = Response(
            self.transport, 404, http_version=message.version, close=True)

        body = b'Page Not Found Hello!'

        response.add_headers(
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(body))))
        response.send_headers()
        response.write(body)
        response.write_eof()

        self.keep_alive(False)
        self.log_access(404, message)


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
