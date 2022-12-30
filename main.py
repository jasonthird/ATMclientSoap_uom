import decimal

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from decimal import *
from kivy.config import Config
from clientLib import Atm

getcontext().prec = 23
getcontext().rounding = decimal.ROUND_DOWN

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # disable the right click red dot

wsldUrl = "http://localhost:8081/AtmEndpoint/soap11/description"
atm = None
authCode = None


def popupError(String):
    app = App.get_running_app()
    popuperror = Popup(title='Error', content=Label(text=String), size_hint=(None, None),
                       size=(app.root.width / 2, app.root.height / 2))
    popuperror.open()


def popupSuccess(String):
    app = App.get_running_app()
    popupsuccess = Popup(title='Success', content=Label(text=String), size_hint=(None, None),
                         size=(app.root.width / 2, app.root.height / 2))
    popupsuccess.open()


class AuthPage(Screen):
    def __init__(self, **kwargs):
        super(AuthPage, self).__init__(**kwargs)

    def auth(self, name, pin):
        global atm
        global authCode
        try:
            if pin == "" or name == "":
                popupError("Please fill in all fields")
            elif not pin.isdigit():
                popupError("Pin must be a number")
            else:
                atm = Atm(wsldUrl)
                authResponce = atm.auth(name, pin)
                if authResponce.success:
                    authCode = authResponce.token
                    self.manager.current = "choose"
                    self.manager.get_screen("choose").updateBalance()
                else:
                    popupError("Auth failed")

        except Exception as e:
            print(e)
            popupError("Server is offline")


class ChoosePage(Screen):
    def updateBalance(self):
        try:
            balance = atm.balance(authCode)
            if balance.success != "False":
                money = round(Decimal(balance.balance), 2)
                self.ids.balance.text = str(money)
            else:
                popupError("Error with request")
        except Exception as e:
            print(e)
            popupError("Server is offline")

    def withdraw(self):
        # change to withdraw page and pass authcode
        self.manager.current = 'withdraw'

    def deposit(self):
        self.manager.current = 'deposit'


class WithdrawPage(Screen):
    def withdraw(self, value):
        try:
            if value == "":
                popupError("Please fill in the value field")
            else:
                try:
                    value = Decimal(value)
                    withdrawResponse = atm.withdraw(authCode, value)
                    if withdrawResponse != 0:
                        popupSuccess("You have successfully withdrawn: " + withdrawResponse)
                        self.manager.current = 'choose'
                        self.manager.get_screen('choose').updateBalance()
                    else:
                        popupError("Error with request")
                except Exception as e:
                    print(e)
                    popupError("Please enter a valid number")
        except Exception as e:
            print(e)
            popupError("Server is offline")

    def back(self):
        self.manager.current = 'choose'
        self.manager.get_screen('choose').updateBalance()


class DepositPage(Screen):
    def deposit(self, value):
        try:
            if value == "":
                popupError("Please fill in the value field")
            else:
                try:
                    value = Decimal(value)
                    depositResponse = atm.deposit(authCode, Decimal(value))
                    if depositResponse != 0:
                        popupSuccess("You have successfully deposited: " + depositResponse)
                        self.manager.current = 'choose'
                        self.manager.get_screen('choose').updateBalance()
                    else:
                        popupError("Error with request")
                except Exception as e:
                    print(e)
                    popupError("Please enter a valid number")
        except Exception as e:
            print(e)
            popupError("Server is offline")

    def back(self):
        self.manager.current = 'choose'
        self.manager.get_screen('choose').updateBalance()


class AtmApp(App):
    def build(self):
        sm = ScreenManager()
        screen1 = AuthPage()
        screen2 = ChoosePage()
        screen3 = WithdrawPage()
        screen4 = DepositPage()
        sm.add_widget(screen1)
        sm.add_widget(screen2)
        sm.add_widget(screen3)
        sm.add_widget(screen4)
        return sm


if __name__ == '__main__':

    # get server ip from terminal argument
    import sys

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = sys.argv[2]

    AtmApp().run()
