from twinelib import story_from_dict, render_story

# Your input dictionary
data = {
    "story_name": "ChatGPT - Dragon Story - 2023.09.19",
    "passages": [
        {
            "name": "Start",
            "content": [
                "You find yourself standing at the entrance of a dark forest.",
                "The path splits into two: one leading deeper into the woods, and the other leading to a nearby village.",
                {
                    "choices": {
                        "Enter the forest": "Forest",
                        "Go to the village": "Village"
                    }
                }
            ]
        },
        {
            "name": "Forest",
            "content": [
                "The trees are dense and the path is overgrown. As you walk, you hear a faint crying sound.",
                "Following the sound, you come across a baby dragon, trapped under some fallen branches.",
                {
                    "choices": {
                        "Help the dragon": "HelpDragon",
                        "Leave the forest": "Start"
                    }
                }
            ]
        },
        {
            "name": "Village",
            "content": [
                "The village is bustling with activity. You see a blacksmith, a tavern, and a magic shop.",
                {
                    "choices": {
                        "Visit the blacksmith": "Blacksmith",
                        "Go to the tavern": "Tavern",
                        "Enter the magic shop": "MagicShop",
                        "Return to the forest": "Start"
                    }
                }
            ]
        },
        {
            "name": "HelpDragon",
            "content": [
                "You free the baby dragon and it nuzzles you in gratitude.",
                "The dragon's mother appears, a majestic creature with shimmering scales.",
                "She thanks you for saving her child and offers to grant you a wish.",
                {
                    "choices": {
                        "Wish for wealth": "Wealth",
                        "Wish for wisdom": "Wisdom",
                        "Wish for adventure": "Adventure"
                    }
                }
            ]
        },
    ]
}

# Create a Story instance from the dictionary.
story = story_from_dict(data)

# Render the HTML.
html_output = render_story(story)

# Save the output to a file.
with open("dragon_story.html", "w", encoding="utf-8") as f:
    f.write(html_output)
