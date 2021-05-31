# -*- coding: utf-8 -*-
import asyncio, aiomysql

import logging

def log(sql, args = ()):
    logging.info('SQL: %s' %sql)

#创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。
#连接池由全局变量__pool存储，缺省情况下将编码设置为utf8，自动提交事务.

async def create_pool(loop, **kw):
    logging.info('creating a database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        user = kw['user'],
        password = kw['password'],
        db = kw['db'],
        #charset = kw.get('charset', 'utf-8'),
        autocommit = kw.get('autocommit', True),
        #maxsize = kw.get('maxsize', 10),
        #minsize = kw.get('minsize',1),
        loop = loop
    )

#把常用的SELECT、INSERT、UPDATE和DELETE操作用函数封装起来,利于代码复用,维护。

async def select(sql, args, size = None):
    log(sql, args)
    global __pool
    # 异步等待连接池对象返回可以连接线程，with语句则封装了清理（关闭conn）和处理异常的工作
    async with __pool.acquire() as conn:
        # 打开一个DictCursor，它与普通游标的不同在于，以dict形式返回结果
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # 将sql中的'?'替换为'%s'，因为mysql语句中的占位符为%s
            #注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击, that is to say, use "$stmt = $mysqli->prepare("DELETE FROM planet WHERE name = ?"); $stmt->bind_param('s', "earth"); $stmt->execute();" instead of "DELETE FROM planet WHERE name = 'earth';"
            await cur.execute(sql.replace('?','%s'), args)
            if size:
                rs = await cur.fetchmany(size) #rs for result set. 
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: {0}'.format(len(rs)))
        return rs

async def execute(sql, args, autocommit = True):
    log(sql)
    async with __pool.acquire() as conn:
        if not autocommit:
            await conn.begin()
        try:
            #For aiomysql.DictCursor, see the explaination in select.py.
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
                if not autocommit:
                    await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise e
        return affected

class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>'%(self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
    def __init__(self, name = None, primary_key = False, default = None, ddl = 'varchar(100)'):
        #One benefit of indirection is that we don’t have to specify the delegate class by name. If you edit the source code to switch the base class to some other mapping, the super() reference will automatically follow. 
        super().__init__(name, ddl, primary_key, default)

class BoolenField(Field):
    def __init__(self, name = None, default = False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):
    def __init__(self, name = None, primary_key = False, default = 0):
        super().__init__(name, 'int', primary_key, default)

class FloatField(Field):
    def __init__(self, name = None, primary_key = False, default = 0.0):
        super().__init__(name, 'real', primary_key, default)

class TextField(Field):
    def __init__(self, name = None, default = None):
        super().__init__(name, 'text', False, default)

class ModelMetaclass(type):        
    def __new__(cls, name, bases, attrs):
        # 排除Model类本身:
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        # 获取table名称:
        #or: if __table__ exists, then tablename is from attrs.get, otherwise name.
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table %s).' % (name, tableName))
        # 获取所有的Field和主键名:
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found mapping: %s ==> %s' % (k,v))
                mappings[k] = v
                # 找到主键:
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: %s.' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '%s' % f, fields))
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__fields__'] = fields
        attrs['__select__'] = 'select `%s`, %s from `%s`;' %(primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s);' % (tableName, ', '.join(escaped_fields), primaryKey, ', '.join('?'*(len(escaped_fields)+1)))
        attrs['__update__'] = 'update `%s` set %s where `%s` = ?' % (tableName, ', '.join(map(lambda f: '%s = ?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s` = ?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)

#定义ORM映射的基类Model
#Model从dict继承，所以具备所有dict的功能
class Model(dict, metaclass = ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute %s"%key)
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def getValue(self, key):
        #The getattr() method returns the value of the named attribute of an object. If not found, it returns the default value provided to the function.
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s.'%(key, str(value)))
                setattr(self, key, value)
        return value

    #往Model类添加class方法，就可以让所有子类调用class方法
    @classmethod
    async def find(cls, pk):
        rs = await select('%s where %s = ?;' %(cls.__select__, cls.__primary_key__
        ), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])
    
    @classmethod
    async def findAll(cls, where = None, args = None, **kw):
        sql = [cls.__select__]
        if where:
            sql.append('where ')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by ')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit ')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where = None, args = None):
        sql = ['select %s _num_ from %s' %(selectField, cls.__table__)]
        if where:
            sql.append('where ')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s.' % rows)
    
    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)