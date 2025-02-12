import json
import os
from socket import gethostname

"""
Usage
-----
- Running this script in a `python dirs.py` fashion allows for an interactive set up 
  of local directories.
- Same happens by running `dirs.configure_system(interactive=True);` after importing 
  the module. For changes to be noticeable, module will need to be imported again.
- Alternatively, running `import dirs` automatically looks for the local directories, 
  and creates options by default if the system is not recognized.
- Once imported, global variables such as `dirs.SYSTEM_HOME` will point to the 
  automatically detected local directories.

Warnings
--------
- Local directories will be automatically created whenever the locally indicated 
  path variables point to non-existent directories.
"""

SYSTEM_HOME = os.getcwd()

DEFAULT_SYSTEM = dict(
    system_name = "DEF", # PC identifier
    system_home = SYSTEM_HOME, # Code repository's directory
    data_home = os.path.join(SYSTEM_HOME, "data"), # Data storage directory
    models_home = os.path.join(SYSTEM_HOME, "models"), # Models storage directory
    results_home = os.path.join(SYSTEM_HOME, "results"), # Results storage directory
)

UNKNOWN_SYSTEM = dict(**DEFAULT_SYSTEM); UNKNOWN_SYSTEM["system_name"] = "UKN"

#%%

def get_systems_filepath(system_home=SYSTEM_HOME):
    """Returns filepath to JSON file containing system directories"""

    return os.path.join(system_home, "dirs.json")

#%%

def check_directories_file(system_home=SYSTEM_HOME):
    """Check if directories' file has been correctly created; fixes it if not"""

    filepath = get_systems_filepath(system_home)

    try:
        with open(filepath, "r") as file:
            systems_dict = json.load(file)
    except:
        systems_dict = {}

    try: systems_dict["else"]
    except: systems_dict.update({"else": UNKNOWN_SYSTEM})

    with open(filepath, "w") as file:
        json.dump(systems_dict, file)

    return systems_dict

#%%

def configure_system(interactive=False):
    """Configures system for a new """

    if interactive:

        answer = input(f"Is this the correct directory for this code repository? (Y/N)\n{SYSTEM_HOME}\n> ")
        answer = "y" in answer.lower()
        if answer:
            system_home = SYSTEM_HOME
        else:
            system_home = input("Copy and paste your code repository directory;\n"+
                                "e.g. /home/user/code/MindEye\n> ")
            
    else: system_home = UNKNOWN_SYSTEM["system_home"]

    if not os.path.isdir(system_home): raise OSError("System directory not found")

    systems_dict = check_directories_file(system_home)

    id = gethostname()
    
    try: 
        system_dict = systems_dict[id]
    except: 
        system_dict = DEFAULT_SYSTEM

    if interactive:

        answer = input(f"Is this the correct nickname for this PC? (Y/N)\n{system_dict['system_name']}\n> ")
        answer = "y" in answer.lower()
        if answer:
            system_name = system_dict["system_name"]
        else:
            system_name = input("Choose a nickname for this PC; e.g. MYPC\n> ")

        answer = input(f"Is this the correct directory for data in this PC? (Y/N)\n{system_dict['data_home']}\n> ")
        answer = "y" in answer.lower()
        if answer:
            data_home = system_dict["data_home"]
        else:
            data_home = input("Copy and paste your data and datasets main directory;\n"+
                            "e.g. /home/user/data/MindEye\n> ")

        answer = input(f"Is this the correct directory for computational models? (Y/N)\n{system_dict['models_home']}\n> ")
        answer = "y" in answer.lower()
        if answer:
            models_home = system_dict["models_home"]
        else:
            answer = input(f"Is this the correct directory for computational models? (Y/N)\n{data_home}\n> ")
            answer = "y" in answer.lower()
        if answer:
            models_home = data_home
        else:
            models_home = input("Copy and paste your computational models directory;\n"+
                                "e.g. /home/user/models/MindEye\n> ")

        answer = input(f"Is this the correct directory for results? (Y/N)\n{system_dict['results_home']}\n> ")
        answer = "y" in answer.lower()
        if answer:
            results_home = system_dict["results_home"]
        else:
            answer = input(f"Is this the correct directory for results? (Y/N)\n{data_home}\n> ")
            answer = "y" in answer.lower()
        if answer:
            results_home = data_home
        else:
            results_home = input("Copy and paste your results directory;\n"+
                                "e.g. /home/user/results/MindEye\n> ")
        
        system_dict.update( dict(
            system_name = system_name,
            system_home = system_home,
            data_home = data_home,
            models_home = models_home,
            results_home = results_home,
        ) )

    if id in systems_dict.keys():
        systems_dict[id].update( system_dict )
    else:
        systems_dict.update({id: system_dict})

    filepath = get_systems_filepath(system_home)
    with open(filepath, "w") as file:
        json.dump(systems_dict, file)
    
    return system_dict

#%% 

def get_system_name():
    """Returns system name according to which PC is running"""
    
    id = gethostname()
    try: return SYSTEM_DICT[id]["system_name"]
    except: 
        try: return SYSTEM_DICT["else"]["system_name"]
        except: raise ValueError("Your PC's nickname must appear inside system name definition")

def get_system_home():
    """Returns home path for repository according to which PC is running"""
    
    id = gethostname()
    try: return SYSTEM_DICT[id]["system_home"]
    except: 
        try: return SYSTEM_DICT["else"]["system_home"]
        except: raise ValueError("Your PC must appear inside syshome definition")

def get_data_home():
    """Returns home path for data according to which CPU is running"""
    
    id = gethostname()
    try: return SYSTEM_DICT[id]["data_home"]
    except: 
        try: return SYSTEM_DICT["else"]["data_home"]
        except: raise ValueError("Your PC must appear inside data home definition")

def get_models_home():
    """Returns models path for models according to which CPU is running"""
    
    id = gethostname()
    try: return SYSTEM_DICT[id]["models_home"]
    except: 
        try: return SYSTEM_DICT["else"]["models_home"]
        except: raise ValueError("Your PC must appear inside models home definition")

def get_results_home():
    """Returns home path for results according to which CPU is running"""
    
    id = gethostname()
    try: return SYSTEM_DICT[id]["results_home"]
    except: 
        try: return SYSTEM_DICT["else"]["results_home"]
        except: raise ValueError("Your PC must appear inside results home definition")

#%%

if __name__ == '__main__':
    SYSTEM_DICT = configure_system(interactive=True)

else:
    while True:
        try:
            SYSTEM_DICT = configure_system()
            break
        except:
            raise ValueError("Please define directories in `dirs.json`")
    
SYSTEM_NAME = SYSTEM_DICT["system_name"]
SYSTEM_HOME = SYSTEM_DICT["system_home"]
DATA_HOME = SYSTEM_DICT["data_home"]
MODELS_HOME = SYSTEM_DICT["models_home"]
RESULTS_HOME = SYSTEM_DICT["results_home"]

if not os.path.isdir(SYSTEM_HOME):
    raise OSError("System directory does not exist")

if not os.path.isdir(DATA_HOME):
    os.makedirs(DATA_HOME)
    print("Data folder was not found so it has been created")

if not os.path.isdir(MODELS_HOME):
    os.makedirs(MODELS_HOME)
    print("Models folder was not found so it has been created")

if not os.path.isdir(RESULTS_HOME):
    os.makedirs(RESULTS_HOME)
    print("Results folder was not found so it has been created")