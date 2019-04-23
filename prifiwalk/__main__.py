from py.function import setup_logger
from py.function import save_object
from py.function import restore_object
from py.config import logfile, logname
from py.database import Database
from py.system import System
from sys import exit
from os import geteuid


logger = setup_logger(logname, logfile)


def menu():
    print("Choose your mode of operation:")
    print("1) Only gather for later processing")
    print("2) Process all collected metadata")
    print("3) Both gather and process")
    print("q) Quit")
    option = input()
    if option.isnumeric() and int(option) in [1, 2, 3]:
        return int(option)
    elif option is "q":
        exit()


def run(mode):
    if mode == 1:
        gather()
    elif mode == 2:
        process()
    elif mode == 3:
        do_both()


def gather():
    system = System(mode='half')
    save_object(str(system.start_measurement), system)


def process():
    db = Database()


def do_both():
    db = Database()
    system = System(mode='full')
    db.store(system)


if __name__ == '__main__':
    euid = geteuid()
    if euid != 0:
        print("You are trying to run PriFiwalk with a non-root user!")
        print("Most PriFiwalk functions need root privileges to work.")
        exit()

    mode = menu()
    run(mode)
