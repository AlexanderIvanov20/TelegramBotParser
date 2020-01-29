from os import system
from time import sleep
import os.path

from datetime import datetime
from pytz import timezone
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


while 1:
    if datetime.time(datetime.now(timezone('Europe/Kiev'))).hour in [10, 15]:
        print('Executing now...')
        executable = os.path.join(BASE_DIR, 'venv', 'Scripts', 'python')
        program = os.path.join(BASE_DIR, 'main', 'Parser.py') + ' ' + 'add'
        system('{} {}'.format(executable, program))
        print('Sleeping...')
        sleep(3600)
    else:
        print('Waiting for suitable time')
