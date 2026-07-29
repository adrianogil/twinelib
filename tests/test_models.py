import unittest

from twinelib import Passage


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


if __name__ == "__main__":
    unittest.main()
