#Here we create food class.
#A food class should includes type, quantity, expiration date, nutrition fact, and others
#category = cat, type = ty, quantity = quan, expiration date = date, nutrition fact = nutri, other = other
#Values of category should be entree, meat, vagetable, spice
#Values of type should be strings inputed by the user, which should specify about food more than categories.
#Values of quantity should be a list, float and string. In particular, the units should be inputed by the users.
#Values of date should be able to update daily. For meat and vegetable, there shall be not expiration date. Thus use the date produced instead.
#Nutrition facts can be N/A.
#Other is for specifying more information that is not specified enough by type.
from datetime import date as d
from datetime import datetime

class Food(object):
    def __init__(self, ID = 'null', *, cat, ty, quan, unit, date, nutri, other):
        #No access to users
        self.__ID = ID
        self.__cat = cat #entree, meat, vegetable, spices,
        self.__ty = ty 
        self.__quan = quan #quan = quantity, quantity with float value,
        self.__unit = unit #unit, for example a bag, a pound, etc.
        self.__date = date #date = [year, month, day] with int values.
        self.__nutri = nutri #nutri = {nutrition fact: [float, unit]}
        self.__other = other         

#get method to have access to the attributions.
    def get(self):
        return {
            'ID':self.__ID, 
            'cat':self.__cat,
            'ty':self.__ty,
            'quan':self.__quan,
            'unit':self.__unit,
            'date':self.__date,
            'nutri':self.__nutri,
            'other':self.__other}

#Update food status.
    def update(self, **kw):
        if 'cat' in kw:
            self.__cat = kw['cat']
            print('The category is updated.')
        elif 'ty' in kw:
            self.__ty = kw['ty']
            print('The type is updated.')
        elif 'quan' in kw:
            self.__quan = kw['quan']
            print('The quantity is updated.')
        elif 'unit' in kw:
            self.__unit = kw['unit']
            print('The unit is updated.')
        elif 'date' in kw:
            self.__date = kw['date']
            print('The expiration date is updated.')
        elif 'nutri' in kw:
            self.__nutri = kw['nutri']
            print('The nutrition fact is updated.')
        elif 'other' in kw:
            self.__other = kw['other']
            print('The other information is updated.')
        else:
            print('Please enter a valid input.')

#Remaining days
    def remaining_days(self):
        if self.__cat not in ('meat', 'vegetable'):
            return (d(datetime.now().year, datetime.now().month, datetime.now().day)-d(self.__date[0], self.__date[1], self.__date[2])).days
        else:
            return -(d(datetime.now().year, datetime.now().month, datetime.now().day)-d(self.__date[0], self.__date[1], self.__date[2])).days

#Warn the users on the low quantity and coming expiration date.
    def warnings(self): 
        if self.__quan < 1:
            return 'Refill %s. There is %s %s remaining.' %(self.__ty+' '+self.__cat, self.__quan, self.__unit)
        if (self.__cat not in ('meat', 'vegetable')) and (self.remaining_days()<5):
            return 'Refill %s. The expiration date is coming in %s days.' %(self.__ty+' '+self.__cat, self.remaining_days())
        if (self.__cat == 'vegetable') and (self.remaining_days()>3):
            return 'It has been %s days since you bought %s. Use it as soon as possible.' %(self.__remaining_days(), self.__ty)
        if (self.__cat == 'meat') and (self.remaining_days()>5):
            return 'It has been %s days since you bought %s. Use it as soon as possible.' %(self.__remaining_days(), self.__ty)
        