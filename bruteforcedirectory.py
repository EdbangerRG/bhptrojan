import queue
import requests
import threading
import sys

AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
EXTENSIONS = ['.php', '.bak', '.orig', '.inc']
TARGET = "http://testphp.vulnweb.com"
THREADS = 50
WORDLIST = "/home/kali/bhp/chapter 5/SVNDigger/SVNDigger/all.txt"

def get_words(resume=None): #returns the words queue we'll test on the target

    def extend_words(word): #this is a inner function that defined within the function above. The purpose of the inner function is to test for the extensions
        if "." in word:
            words.put(f'/{word}')
        else:
            words.put(f'/{word}/')

        for extensions in EXTENSIONS:
            word.put(f'/{word}{extensions}')
    with open(WORDLIST) as f:
        raw_words = f.read() #read the wordlist file and begin iterating over each line
    found_resume = False
    words = queue.Queue()
    for word in raw_words.split():
        if resume is not None: #return to the last path that the brute force tried.
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                print(f'Resuming wordlist from: {resume}')
            else:
                print(word)
                extend_words(word)
        return words # this is the function that allows brute force 
def dir_bruter(words):
    headers = {'User-Agent': AGENT}
    while not words.empty():
        url = f'{TARGET}{words.get()}'
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            sys.stderr.write('x');sys.stderr.flush()
            continue
        if r.status_code == 200:
            print(f'\nSuccess ({r.status_code}: {url})')
        elif r.status_code == 404:
            sys.stderr.write('.');sys.stderr.flush()
        else:
            print(f'{r.status_code} => {url}')

if __name__== '__main__':
    words = get_words()
    print('Press return to continue.')
    sys.stdin.readline()
    for _ in range(THREADS):
        t = threading.Thread(target=dir_bruter, args=(words,))
        t.start()