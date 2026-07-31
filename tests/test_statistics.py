import unittest

from twinelib import Passage, Story, compute_story_stats


class StoryStatisticsTest(unittest.TestCase):
    def test_connected_graph_counts_passages_and_all_supported_link_forms(self):
        story = Story(
            name="Connected story",
            passages=[
                Passage(
                    name="Start",
                    content="Choose [[North]], [[Go south->South]], or [[East<-Go east]].",
                ),
                Passage(name="North", content="Return [[Start]]."),
                Passage(name="South", content="Return [[Start]]."),
                Passage(name="East", content="Return [[Start]]."),
            ],
        )

        stats = compute_story_stats(story, start_passage="Start")

        self.assertEqual(stats.passage_count, 4)
        self.assertEqual(stats.link_count, 6)
        self.assertEqual(stats.dead_end_passages, [])
        self.assertEqual(stats.unreachable_passages, [])

    def test_dead_end_passages_have_no_outgoing_links(self):
        story = Story(
            name="Dead ends",
            passages=[
                Passage(name="Start", content="Choose [[Win]] or [[Lose]]."),
                Passage(name="Win", content="You win."),
                Passage(name="Lose", content="You lose."),
            ],
        )

        stats = compute_story_stats(story, start_passage="Start")

        self.assertEqual(stats.dead_end_passages, ["Win", "Lose"])

    def test_unreachable_passages_are_reported_from_the_selected_start(self):
        story = Story(
            name="Unreachable branch",
            passages=[
                Passage(name="Start", content="Continue to [[End]]."),
                Passage(name="End", content="Done."),
                Passage(name="Unused", content="Go to [[Unused End]]."),
                Passage(name="Unused End", content="Hidden ending."),
            ],
        )

        stats = compute_story_stats(story, start_passage="Start")

        self.assertEqual(stats.unreachable_passages, ["Unused", "Unused End"])

    def test_broken_links_are_rejected_instead_of_counted(self):
        story = Story(
            name="Broken story",
            passages=[Passage(name="Start", content="Go to [[Missing]].")],
        )

        with self.assertRaisesRegex(
            ValueError, "missing passages: 'Start' -> 'Missing'"
        ):
            compute_story_stats(story, start_passage="Start")

    def test_default_start_passage_uses_startnode_pid(self):
        story = Story(
            name="PID start",
            startnode=2,
            passages=[
                Passage(pid=1, name="Unused", content="Not connected."),
                Passage(pid=2, name="Start", content="Go to [[End]]."),
                Passage(pid=3, name="End", content="Done."),
            ],
        )

        stats = compute_story_stats(story)

        self.assertEqual(stats.unreachable_passages, ["Unused"])


if __name__ == "__main__":
    unittest.main()
