from twinelib import Story, Passage, render_story

# Create passages
passage_start = Passage(
    pid=1,
    name="Start",
    position="175,75",
    size="100,100",
    content=(
        "You find yourself standing at the entrance of a dark forest. "
        "The path splits into two: one leading deeper into the woods, and the other leading to a nearby village.\n"
        "[[Enter the forest->Forest]]\n"
        "[[Go to the village->Village]]"
    )
)

passage_forest = Passage(
    pid=2,
    name="Forest",
    position="475,50",
    size="100,100",
    content=(
        "The trees are dense and the path is overgrown. As you walk, you hear a faint crying sound. "
        "Following the sound, you come across a baby dragon, trapped under some fallen branches.\n"
        "[[Help the dragon->HelpDragon]]\n"
        "[[Leave the forest->Start]]"
    )
)

# Create a story instance
story = Story(
    name="ChatGPT - Dragon Story - 2023.09.19",
    startnode=1,
    ifid="3f672f5c-cfdf-45bc-aec3-bc258889acad",
    passages=[passage_start, passage_forest]
)

# Render the HTML by replacing the placeholders in the template
html_output = render_story(story)

# Save the output to a file
with open("dragon_story.html", "w", encoding="utf-8") as f:
    f.write(html_output)
