# -*- coding: utf-8 -*-
#This is a template of a web app. 
import logging; logging.basicConfig(level = logging.INFO)

#asyncio is a library to write concurrent code using the async/await syntax.
import asyncio, os, json, time
from datetime import datetime

#Asynchronous HTTP Client/Server.
from aiohttp import web

async def index(request):
    return web.Response(body = b'<h1> Hello world!</h1>', content_type = 'text/html')

def init():
    app = web.Application()
    app.router.add_get('/',index)
    web.run_app(app, host = '127.0.0.1', port = 9000)

if __name__ == '__main__':
    init()

#loop = asyncio.get_event_loop()
#loop.run_until_complete(init(loop))
#loop.run_forever