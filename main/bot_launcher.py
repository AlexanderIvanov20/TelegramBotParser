from os import system
from time import sleep
import os.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


while 1:
    executable = os.path.join(BASE_DIR, 'venv' 'Scripts', 'python')
    program = os.path.join(BASE_DIR, 'main', 'FinalBot.py')
    system('{} {}'.format(executable, program))
    print("Restarting now... Press Ctrl-C once again to exit")
    sleep(2)
