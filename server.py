import logging
import os

import aiohttp_jinja2
import asyncio
import jinja2

from aiohttp import web

logger = logging.getLogger(__name__)

@asyncio.coroutine
def index(request):
    response = aiohttp_jinja2.render_template('01_05_2016.html', request, {})
    print("{method} HTTP '{path}' {status}".format(
        method=request.method, path=request.path, status=response.status
    ))
    return response

def start_server(name, server, l):
    s = l.run_until_complete(server)
    print('{} server started on: {}:{}'.format(name, *s.sockets[0].getsockname()))

if __name__ == '__main__':
    app_dir = os.path.dirname(__file__)

    app = web.Application()

    # Setup Jinja2 template engine
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(app_dir))

    # Application routes
    app.router.add_route('GET', '/', index)

    loop = asyncio.get_event_loop()

    # Run http server
    http_server = loop.create_server(app.make_handler(), '127.0.0.1', 5000)
    start_server('HTTP', http_server, loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
        print('Server stoped')
