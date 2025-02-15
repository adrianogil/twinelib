from twinelib import story_from_dict, render_story
import json

data_path = "twinelib/data/dragon_story.json"

# Load the JSON data.
with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Create a Story instance from the dictionary.
story = story_from_dict(data)

# Render the HTML.
html_output = render_story(story)

# Save the output to a file.
with open("dragon_story.html", "w", encoding="utf-8") as f:
    f.write(html_output)
print("Story generated! Open dragon_story.html in your browser to view the story.")
