#Here we create food class.
#A food class should includes type, quantity, expiration date, nutrition fact, and others
#type = ty, quantity = quan, expiration date = date, nutrition fact = nutri, other = other
#Values of type should be strings inputed by the user, which could be rice, meat, or vegetable.
#Values of quantity should be a list, float and string. In particular, the units should be inputed by the users.
#Values of date should be able to update daily.
#Nutrition facts can be N/A.
#Other is for specifying more information that is not specified enough by type.
class food:
    def __init__(self, ty, quan, date, nutri = 'N/A', other = 'N/A'):
        self.ty = ty
        self.quan = quan
        self.date = date
        self.nutri = nutri
        self.other = other
