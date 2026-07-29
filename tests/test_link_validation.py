import unittest

from twinelib import Passage, Story, render_story_data, validate_story_links
from twinelib import extract_link_target, iter_passage_links


class LinkValidationTest(unittest.TestCase):
    def test_extract_link_target_supports_common_twine_link_forms(self):
        self.assertEqual(extract_link_target("Next"), "Next")
        self.assertEqual(extract_link_target("Go north->North Room"), "North Room")
        self.assertEqual(extract_link_target("North Room<-Go north"), "North Room")

    def test_iter_passage_links_returns_all_targets(self):
        self.assertEqual(
            list(
                iter_passage_links(
                    "Go [[North]], [[Go south->South]], or [[East<-Go east]]."
                )
            ),
            ["North", "South", "East"],
        )

    def test_validate_story_links_accepts_existing_targets(self):
        story = Story(
            name="Valid story",
            passages=[
                Passage(
                    name="Start",
                    content="Go [[North]], [[Go south->South]], or [[East<-Go east]].",
                ),
                Passage(name="North", content="Return [[Start]]"),
                Passage(name="South", content="Return [[Start]]"),
                Passage(name="East", content="Return [[Start]]"),
            ],
        )

        validate_story_links(story)

    def test_validate_story_links_rejects_missing_targets_for_each_link_form(self):
        link_forms = (
            "[[Missing]]",
            "[[Go there->Missing]]",
            "[[Missing<-Go there]]",
        )

        for link in link_forms:
            with self.subTest(link=link):
                story = Story(
                    name="Broken story",
                    passages=[Passage(name="Start", content=f"Go {link}.")],
                )

                with self.assertRaisesRegex(
                    ValueError, "missing passages: 'Start' -> 'Missing'"
                ):
                    validate_story_links(story)

    def test_validate_story_links_rejects_empty_targets(self):
        malformed_links = ("[[]]", "[[Go there->]]", "[[<-Go there]]")

        for link in malformed_links:
            with self.subTest(link=link):
                story = Story(
                    name="Broken story",
                    passages=[Passage(name="Start", content=f"Go {link}.")],
                )

                with self.assertRaisesRegex(
                    ValueError, "missing passages: 'Start' -> ''"
                ):
                    validate_story_links(story)

    def test_render_story_data_rejects_missing_targets_before_rendering(self):
        story = Story(
            name="Broken story",
            passages=[
                Passage(name="Start", content="Go [[Missing]]."),
            ],
        )

        with self.assertRaisesRegex(ValueError, "missing passages: 'Start' -> 'Missing'"):
            render_story_data(story)

    def test_validate_story_links_rejects_duplicate_passage_names(self):
        story = Story(
            name="Duplicate story",
            passages=[
                Passage(name="Start", content="Go [[Start]]."),
                Passage(name="Start", content="Duplicate."),
            ],
        )

        with self.assertRaisesRegex(ValueError, "Duplicate passage names found: Start"):
            validate_story_links(story)


if __name__ == "__main__":
    unittest.main()
