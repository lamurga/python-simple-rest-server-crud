import sqlobject
from Connection import conn


class User(sqlobject.SQLObject):
    _connection = conn
    email = sqlobject.StringCol(length=100, unique=True)
    firstname = sqlobject.StringCol(length=100)
    lastname = sqlobject.StringCol(length=100)
    address = sqlobject.StringCol(length=255)


User.createTable(ifNotExists=True)
