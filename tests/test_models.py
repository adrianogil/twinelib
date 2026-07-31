import unittest
from copy import deepcopy

from twinelib import Passage, story_from_dict


class PassageTest(unittest.TestCase):
    def test_structured_content_is_converted_to_twine_markup(self):
        passage = Passage(
            name="Start",
            content=[
                "Choose a path.",
                {"choices": {"Go north": "North", "Go south": "South"}},
            ],
        )

        self.assertEqual(
            passage.content,
            "Choose a path.\n[[Go north->North]]\n[[Go south->South]]",
        )


class StoryFromDictTest(unittest.TestCase):
    def test_story_conversion_does_not_mutate_caller_input(self):
        data = {
            "story_name": "Paths",
            "passages": [
                {"name": "Start", "content": "Choose [[North]]."},
                {"name": "North", "content": "The northern path."},
            ],
        }
        original_data = deepcopy(data)

        first_story = story_from_dict(data)
        second_story = story_from_dict(data)

        self.assertEqual(data, original_data)
        self.assertEqual([passage.pid for passage in first_story.passages], [1, 2])
        self.assertEqual([passage.pid for passage in second_story.passages], [1, 2])


if __name__ == "__main__":
    unittest.main()
