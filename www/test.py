import asyncio
import db_orm as orm
from Model import User

loop = asyncio.get_event_loop()
async def test(loop):
    await orm.create_pool(loop, user = 'www-data', password = 'www-data', db = 'awesome')
    await User.findAll()

loop.run_until_complete(test(loop))