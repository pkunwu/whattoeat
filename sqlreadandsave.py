#store datas on mysql
import mysql.connector

def login():
    user = input('Please input user name: ')
    password = input('Please input password: ')
    try:
#Try login.
        conn = mysql.connector.connect(user = user, password = password)
    except mysql.connector.errors.ProgrammingError as e:
        print('Error %s.'%(e))

    cursor = conn.cursor()
    try:
        cursor.execute('use whattoeat;')
#if whattoeat database does not exist, then we create one, select it, and create tables, since it is the first time user use it.
    except mysql.connector.errors.ProgrammingError:
        conn = mysql.connector.connect(user = user, password = password)
        cursor = conn.cursor()
        #Table food contains collumn id as primary key.
        cursor.execute('create database whattoeat; use whattoeat; create table food (ID int not null auto_increment, category varchar(20), type varchar(20), quantity varchar(4), unit varchar(20), expiration varchar(20), nutrition varchar(20), other varchar(20), primary key (ID));')
        #for now, let's just create food table, with limited columns. This may be changed later.
    finally:
        cursor.close()
        print('Table food is ready.')
    try:
        return conn
    except UnboundLocalError:
        pass    

#read values from the table according to the inputs. Return a GENERATOR, since we only deal with data one by one. We do not allow read items from Table food by id.
def read(**kw):
    data = []
    #Suppose mysql is connected. Otherwise, connect to mysql.
    try:
        kw['conn'].reconnect()
        cursor = kw['conn'].cursor()
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
            #We do not allow read items by id.
            cursor.execute('select * from food where %s = \"%s\";', [key, kw[key]])
            col = cursor.column_names
            #if the selected value is empty, then print no such value.
            if cursor.fetchall() == []: 
                print('There is no such value (%s,%s) in the table.' %(key, kw[key]))
            else:
                data.append(cursor.fetchall())
        except mysql.connector.errors.ProgrammingError as e:
            print('Error: ' + e + 'when fetching %s = %s.' %(key, kw[key]))

        cursor.close()

        return [todict(col = col, data = item) for item in data]

#Transform the data to dictionary so that later a list of food object can be created easily.
def todict(*,col,data):
    #Data should be just ONE row from the table.
    #Return a dictionary, where keys are from col and values are from data. So col and data MUST be arranged!
    return {col[i]: data[i] for i in range(len(col))}

#save several rows to the table that are combined in a list and entered using key word data. The input should be a food objects. Id is used to determine if the data is saved or new. If the data is saved and we want to update it, then its id shall remain the same. If the data is new and we want to save it, then the value of its id shall be null.
def save(**kw):
    #Suppose mysql is connected. Otherwise, connect to mysql.
    try:
        kw['conn'].reconnect()
        cursor = kw['conn'].cursor()
    except:
        print('Please login.')

    data = kw['data']
    cursor.execute('use whattoeat;')
    
    #Save data to mysql.
    for i in range(len(data)):
        try:
            cursor.execute('insert into food (ID, category, type, quantity, unit, expiration, nutrition, other) values ({0}, \"{1}\", \"{2}\", \"{3}\", \"{4}\", \"{5}\", \"{6}\", \"{7}\") on duplicate key update category = \"{1}\", type = \"{2}\", quantity = \"{3}\", unit = \"{4}\", expiration = \"{5}\", nutrition = \"{6}\", other = \"{7}\";'.format(data[i]['ID'], data[i]['cat'], data[i]['ty'], data[i]['quan'], data[i]['unit'], data[i]['date'], data[i]['nutri'], data[i]['other']))
        except mysql.connector.errors.ProgrammingError as e:
            print('Error: {0} when saving the {1} item.'.format(e, i))
            
    cursor.close()

#Delete a row from Table food. Ideally, we only delete a row by its ID.
def delete(**kw):
    #Suppose mysql is connected. Otherwise, connect to mysql.
    try:
        kw['conn'].reconnect()
        cursor = kw['conn'].cursor()
    except:
        print('Please login.')
    
    #The IDs of the rows we want to delete are entered using key word data.
    data = kw['data']
    cursor.execute('use whattoeat;')

    for i in range(len(data)):
        try:
            cursor.execute('delete from food where id ={0};'.format(data[i]))
        except mysql.connector.errors.ProgrammingError as e:
            print('Error: {0} when deleting the item with ID = {1}.'.format(e, data[i]))
    cursor.close()
