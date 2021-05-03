#store datas on mysql
import mysql.connector

def login():
    user = input('Please input user name: ')
    password = input('Please input password: ')
    try:
#if whattoeat database exists, then we select it.
        conn = mysql.connector.connect(user = user, password = password, database = 'whattoeat')
        cursor = conn.cursor()
#if whattoeat database does not exist, then we create one, select it, and create tables, since it is the first time user use it.
    except mysql.connector.errors.ProgrammingError:
        conn = mysql.connector.connect(user = user, password = password)
        cursor = conn.cursor()
        cursor.execute('create database whattoeat; use whattoeat; create table food (id varchar(5), category varchar(20), type varchar(20), quantity varchar(4), unit varchar(20), expiration varchar(20), nutrition varchar(20), other varchar(20));')
        #for now, let's just create food table, with limited columns. This may be changed later.
    finally:
        print('Table food is ready.')

#read values from the table according to the inputs. Return a GENERATOR, since we only deal with data one by one.
def read(**kw):
    data = []
    #Suppose mysql is connected. Otherwise, connect to mysql.
    try:
        cursor.reset()
    except:
        print('Please login.')
    # when there is no key word parameter, return everything in the table.
    if kw == {}: 
        try:
            cursor.execute('select * from food;')
            #if there is nothing in the table, then print it out.
            if cursor.fetchall() == []: 
                print('There is no saved data.')
            else:
                #else, save the data and column names.
                data = cursor.fetchall()
                col = cursor.column_names
        finally:
            cursor.reset()
    for key in kw: #read one value at a time.
        try:
            #select the value from the table and save the column names as col.
            cursor.execute('select * from food where %s = %s;', [key, kw[key]])
            col = cursor.column_names
            #if the selected value is empty, then print no such value.
            if cursor.fetchall() == []: 
                print('There is no such value (%s,%s) in the table.' %(key, kw[key]))
            else:
                data.append(cursor.fetchall())
        except mysql.connector.errors.ProgrammingError as e:
            print('Error: ' + e + 'when fetching %s = %s' %(key, kw[key]))
        finally:
            cursor.reset()
        #Id is saved as first column, the rest is saved as the second columns, so that later food can directly be applied to it. 
        for item in data:
            yield {item[0], todict(col = col[1:], data = item[1:])}
#Transform the data to dictionary so that later a list of food object can be created easily.
def todict(*,col,data):
    #Data should be just ONE row from the table.
    #Return a dictionary, where keys are from col and values are from data. So col and data MUST be arranged!
    return {col[i]: data [i] for i in range(len(col))}

#save values to the table. The input should be a list of food objects. 
def save(**kw):
    #Suppose mysql is connected. Otherwise, connect to mysql.
    try:
        cursor.reset()
    except:
        print('Please login.')
    #The number of rows in the table.
    cursor.execute('select id from food;')
    n = len(cursor.fetchall())
    for item in kw['data']:
        try:
            #Save data to sql. If there is a duplicate key then update. Thus when load the data and assign id to food, id must be different.
            cursor.execute('insert into food (id, category, type, quantity, unit, expiration, nutrition, other) values (%s, %s, %s, %s, %s, %s, %s, %s) on duplicate key update category = %s, type = %s, quantity = %s, unit = %s, expiration = %s, nutrition = %s, other = %s;'%(item['id'], item['cat'], item['id'], item['ty'], item['quan'], item['unit'], item['date'], item['nutri'], item['other'], item['cat'], item['id'], item['ty'], item['quan'], item['unit'], item['date'], item['nutri'], item['other']))
