# example usage and client library for the server

from zeep import Client


class Atm(object):
    def __init__(self, wsdlUrl):
        self.client = Client(wsdlUrl)

    def auth(self, username, pin):
        return self.client.service.Auth(username, pin)

    def balance(self, auth):
        return self.client.service.Balance(auth)

    def withdraw(self, auth, amount):
        return self.client.service.Withdraw(auth, amount)

    def deposit(self, auth, amount):
        return self.client.service.Deposit(auth, amount)




""" example usage
atm = Atm()

x = atm.auth("userbbrgf", 8152)
print(x)
print(atm.balance(x))
print(atm.withdraw(x, 100))
print(atm.balance(x))
print(atm.deposit(x, 100))
print(atm.balance(x))

"""
