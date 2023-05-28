import contextlib
import os
import queue
import requests
import sys
import threading
import time

FILETED = [".jpg", ".gif", ".png", ".css"]
TARGET = "http://boodelyboo.com/wordpress" #Define the website we want to attack
THREADS = 10

answers = queue.Queue() # This stores the files we located locally.
web_paths = queue.Queue() # This stores files on the remote server.

def gather_paths(): # This is similiar to a crawler where we walk around in the different directories  and build the full path and test them against the list in FILTETED.
    for root, _, files in os.walk('.'):
        for fname in files:
            if os.path.splitext(fname)[1] in FILETED:
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'):
                path = path[1:]
            print(path)
            
            web_paths.put(path)
@contextlib.contextmanager
def chdir(path): #this function lets you execute commands from a different directory, when you exit you are returned to your original directory
    """
    On enter, change directory to specific path.
    on exit, change directory back to orginal.
    """
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(this_dir) # reverts to original directory.

def test_remote():
    while not web_paths.get(): # loops until the Queue is empty
        url = f'{TARGET}{path}' # for each iteration we grab a Queue from this and add to the target website
        time.sleep(2) # your target may have throttling/lockout
        r = requests.get(url)
        if r.status_code == 200: # if 200 status code write out to snippet below
            answers.put(url)
            sys.stdout.write('+')
        else:
            sys.stdout.write('x')
        sys.stdout.flush()

def run():
    mythreads = list()
    for i in range(THREADS):
        print(f'Spawning thread {i}')
        t = threading.Thread(target=test_remote)
        mythreads.append(t)
        t.start
    for thread in mythreads:
        thread.join()

if __name__ == '__main__':
    with chdir("/home/kali/"):
        gather_paths()
    input('Press return to continue')

    run()
    with open('myanswer.txt', 'w') as f:
        while not answers.empty():
            f.write(f'{answers.get()}\n')
    print('done')