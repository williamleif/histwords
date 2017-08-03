import sys
import os
import base64
import threading

import ssl
import SocketServer
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

WEB_PORT=5000

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def log_request(self, *args, **kwargs):
        pass

class WebHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        import webhandle
        reload(webhandle)

        webhandle.do_get(self)

    def do_POST(self):
        import webhandle
        reload(webhandle)

        webhandle.do_post(self)


SERVER=None
def serve_http(https_port=80, HandlerClass = WebHandler):
    global SERVER
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = ThreadedTCPServer(("", https_port), HandlerClass)
    debug("Serving HTTP on", https_port)

    SERVER = httpd
    SERVER.serve_forever()

def debug(*args):
    print(" ".join(map(str, args)))

def start():
    port = int(WEB_PORT)

    def run_webserve():
        serve_http(port)

    web_thread = threading.Thread(target=run_webserve)
    web_thread.daemon = True
    web_thread.start()


    return web_thread

def stop():
    SERVER.shutdown()
    SERVER.server_close()

def restart():
    stop()
    start()


def main():
    t = start()
    import helpers

    # TODO: add argument parsing with argparse

    helpers.select_embedding()


    while True:
        t.join(0.5)

        if not t.isAlive():
            print "WEBSERVER DIED, EXITING"
            break

if __name__ == '__main__':
    main()

