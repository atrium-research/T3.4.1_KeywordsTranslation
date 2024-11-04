import sys
import os


# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

#  loading utils
import data_utils
import tools_utils
import main_functions

import importlib
importlib.reload(data_utils)
importlib.reload(tools_utils)
importlib.reload(main_functions)

data = data_utils.get_sample(['en', 'fr', 'pt'], 100)
print(data[0:10])

