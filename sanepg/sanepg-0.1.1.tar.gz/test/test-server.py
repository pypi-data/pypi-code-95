#!/usr/bin/env python3

import asyncio
import logging
import os
import random
import sys

import sanepg
import tornado.ioloop
import tornado.web

logging.basicConfig(
    format  = '%(asctime)s %(levelname)-8s %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
    level   = logging.INFO
    )

class MainHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write('Hello...<br/>')
        self.flush()
        try:
            c = await self.application.db.execute('SELECT 1 as p, pg_sleep(10) as s')
        except sanepg.SaneError as e:
            self.write('%s' % e)
            self.write('<br/>')
            return
        except Exception as ee:
            print()
            print('???', ee)
            print()
        self.write('World')

def main():
    dsn = 'host=localhost user=postgres password=password'

    try:
        db = sanepg.connect(dsn)
    except sanepg.SaneError as e:
        print(e)
        return

    app = tornado.web.Application([
        (r'/', MainHandler),
    ], debug=True)
    app.listen(8888)

    app.db = db

    ioloop = tornado.ioloop.IOLoop.current()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        print()
        ioloop.add_callback(ioloop.stop)

if __name__ == '__main__':
    main()
