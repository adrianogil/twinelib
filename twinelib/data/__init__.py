# Get path of current directory of this file

import os
import json
data_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(data_path, "dragon_story.json")
# Load the JSON data.
with open(data_path, "r", encoding="utf-8") as file_handler:
    data = json.load(file_handler)
