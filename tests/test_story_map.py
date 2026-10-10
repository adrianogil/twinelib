import copy
import re
import unittest

from twinelib import Passage, Story, compute_story_stats, render_story_map


class StoryMapTest(unittest.TestCase):
    def test_public_api_returns_unfenced_mermaid_with_a_final_newline(self):
        story = Story(name="Map", passages=[Passage(name="End", content="Done.")])

        result = render_story_map(story)

        self.assertIsInstance(result, str)
        self.assertEqual(result, 'flowchart TD\n    p0(["End #40;ending#41;"])\n')
        self.assertNotIn("```", result)

    def test_supported_link_forms_preserve_choice_labels_and_targets(self):
        story = Story(
            name="Choices",
            passages=[
                Passage(
                    name="Start",
                    content="[[ North ]] [[ Go south -> South ]] [[ East <- Go east ]]",
                ),
                Passage(name="North", content="The north ending."),
                Passage(name="South", content="The south ending."),
                Passage(name="East", content="The east ending."),
            ],
        )

        result = render_story_map(story)

        self.assertIn('    p0["Start"]\n', result)
        self.assertIn('    p0 -->|"North"| p1\n', result)
        self.assertIn('    p0 -->|"Go south"| p2\n', result)
        self.assertIn('    p0 -->|"Go east"| p3\n', result)
        self.assertEqual(result.count(" -->"), 3)
        self.assertNotIn("unreachable", result)

    def test_structured_content_choices_are_rendered(self):
        story = Story(
            name="Structured content",
            passages=[
                Passage(
                    name="Start",
                    content=["Choose a path.", {"choices": {"Continue": "End"}}],
                ),
                Passage(name="End", content="Done."),
            ],
        )

        self.assertIn('    p0 -->|"Continue"| p1\n', render_story_map(story))

    def test_empty_display_text_produces_an_unlabeled_edge(self):
        for link in ("[[->End]]", "[[End<-]]", "[[  ->End]]", "[[End<-  ]]"):
            with self.subTest(link=link):
                story = Story(
                    name="Empty label",
                    passages=[
                        Passage(name="Start", content=link),
                        Passage(name="End", content="Done."),
                    ],
                )

                self.assertIn("    p0 --> p1\n", render_story_map(story))

    def test_endings_unreachable_nodes_and_their_overlap_are_marked(self):
        story = Story(
            name="Disconnected branch",
            passages=[
                Passage(name="Start", content="[[End]]"),
                Passage(name="End", content="Done."),
                Passage(name="Unused", content="[[Unused End]]"),
                Passage(name="Unused End", content="Done."),
            ],
        )

        result = render_story_map(story)

        self.assertIn('    p1(["End #40;ending#41;"])\n', result)
        self.assertIn('    p2["Unused #40;unreachable#41;"]\n', result)
        self.assertIn(
            '    p3(["Unused End #40;ending, unreachable#41;"])\n', result
        )
        self.assertIn("    classDef unreachable ", result)
        self.assertIn("    class p2,p3 unreachable\n", result)
        self.assertIn('    p2 -->|"Unused End"| p3\n', result)

    def test_unreachable_cycle_has_no_endings(self):
        story = Story(
            name="Isolated cycle",
            passages=[
                Passage(name="Start", content="[[Start]]"),
                Passage(name="A", content="[[B]]"),
                Passage(name="B", content="[[A]]"),
            ],
        )

        result = render_story_map(story)

        self.assertNotIn("ending", result)
        self.assertIn("    class p1,p2 unreachable\n", result)
        self.assertEqual(result.count(" -->"), 3)

    def test_default_start_is_selected_by_pid_even_when_not_first(self):
        story = Story(
            name="PID start",
            startnode=20,
            passages=[
                Passage(pid=10, name="Unused", content="Done."),
                Passage(pid=20, name="Start", content="[[End]]"),
                Passage(pid=30, name="End", content="Done."),
            ],
        )

        result = render_story_map(story)

        self.assertIn("    class p0 unreachable\n", result)
        self.assertNotIn('p1["Start #40;unreachable#41;"]', result)
        self.assertIn('    p2(["End #40;ending#41;"])\n', result)

    def test_stories_without_pids_default_to_first_passage(self):
        story = Story(
            name="No PIDs",
            startnode=99,
            passages=[
                Passage(name="First", content="[[Last]]"),
                Passage(name="Unused", content="Done."),
                Passage(name="Last", content="Done."),
            ],
        )

        self.assertIn("    class p1 unreachable\n", render_story_map(story))

    def test_explicit_start_overrides_story_pid(self):
        story = Story(
            name="Override",
            passages=[
                Passage(pid=1, name="Default", content="[[End]]"),
                Passage(pid=2, name="Other", content="[[Other]]"),
                Passage(pid=3, name="End", content="Done."),
            ],
        )

        self.assertIn(
            "    class p0,p2 unreachable\n",
            render_story_map(story, start_passage="Other"),
        )

    def test_explicit_start_works_when_startnode_pid_is_missing(self):
        story = Story(
            name="Explicit start",
            startnode=99,
            passages=[Passage(pid=1, name="Start", content="Done.")],
        )

        self.assertNotIn("unreachable", render_story_map(story, start_passage="Start"))

    def test_cycles_self_links_and_duplicate_choices_are_preserved(self):
        story = Story(
            name="Cycles",
            passages=[
                Passage(name="A", content="[[A]] [[B]] [[B]] [[Other choice->B]]"),
                Passage(name="B", content="[[A]]"),
            ],
        )

        result = render_story_map(story)

        self.assertEqual(result.count('    p0 -->|"A"| p0\n'), 1)
        self.assertEqual(result.count('    p0 -->|"B"| p1\n'), 2)
        self.assertEqual(result.count('    p0 -->|"Other choice"| p1\n'), 1)
        self.assertEqual(result.count('    p1 -->|"A"| p0\n'), 1)
        self.assertEqual(result.count(" -->"), compute_story_stats(story).link_count)
        self.assertNotIn("ending", result)
        self.assertNotIn("unreachable", result)

    def test_empty_story_returns_a_valid_empty_diagram(self):
        self.assertEqual(
            render_story_map(Story(name="Empty", passages=[])), "flowchart TD\n"
        )

    def test_empty_story_rejects_an_explicit_start(self):
        with self.assertRaisesRegex(ValueError, "Start passage not found"):
            render_story_map(Story(name="Empty", passages=[]), start_passage="Start")

    def test_supported_directions_are_used(self):
        story = Story(name="Empty", passages=[])
        for direction in ("TD", "TB", "BT", "LR", "RL"):
            with self.subTest(direction=direction):
                self.assertEqual(render_story_map(story, direction=direction), f"flowchart {direction}\n")

    def test_invalid_directions_and_direction_injection_are_rejected(self):
        story = Story(name="Empty", passages=[])
        for direction in ("", "td", "UP", " LR", "LR ", "LR\np0 --> p1", None):
            with self.subTest(direction=direction):
                with self.assertRaisesRegex(ValueError, "direction"):
                    render_story_map(story, direction=direction)

    def test_missing_targets_are_rejected_for_all_supported_link_forms(self):
        for link in ("[[Missing]]", "[[Go->Missing]]", "[[Missing<-Go]]"):
            with self.subTest(link=link):
                story = Story(
                    name="Broken", passages=[Passage(name="Start", content=link)]
                )

                with self.assertRaisesRegex(
                    ValueError, "missing passages: 'Start' -> 'Missing'"
                ):
                    render_story_map(story)

    def test_empty_targets_are_rejected_for_all_supported_link_forms(self):
        for link in ("[[]]", "[[ ]]", "[[Go->]]", "[[<-Go]]"):
            with self.subTest(link=link):
                story = Story(
                    name="Broken", passages=[Passage(name="Start", content=link)]
                )

                with self.assertRaisesRegex(
                    ValueError, "missing passages: 'Start' -> ''"
                ):
                    render_story_map(story)

    def test_duplicate_passage_names_are_rejected(self):
        story = Story(
            name="Duplicate names",
            passages=[
                Passage(pid=1, name="Same", content="Done."),
                Passage(pid=2, name="Same", content="Done."),
            ],
        )

        with self.assertRaisesRegex(ValueError, "Duplicate passage names found: Same"):
            render_story_map(story)

    def test_unknown_and_empty_explicit_start_names_are_rejected(self):
        story = Story(name="Map", passages=[Passage(name="Start", content="Done.")])
        for start in ("Missing", "", "start"):
            with self.subTest(start=start):
                with self.assertRaisesRegex(ValueError, "Start passage not found"):
                    render_story_map(story, start_passage=start)

    def test_missing_start_pid_is_rejected_including_mixed_pid_stories(self):
        for other_pid in (2, None):
            with self.subTest(other_pid=other_pid):
                story = Story(
                    name="Missing start PID",
                    startnode=99,
                    passages=[
                        Passage(pid=1, name="One", content="Done."),
                        Passage(pid=other_pid, name="Two", content="Done."),
                    ],
                )

                with self.assertRaisesRegex(ValueError, "startnode pid: 99"):
                    render_story_map(story)

    def test_mermaid_reserved_names_are_labels_not_node_identifiers(self):
        story = Story(
            name="Reserved names",
            passages=[
                Passage(name="end", content="[[p0]]"),
                Passage(name="p0", content="[[classDef]]"),
                Passage(name="classDef", content="Done."),
            ],
        )

        result = render_story_map(story)

        self.assertIn('    p0["end"]\n', result)
        self.assertIn('    p1["p0"]\n', result)
        self.assertIn('    p0 -->|"p0"| p1\n', result)
        self.assertIn('    p1 -->|"classDef"| p2\n', result)

    def test_punctuation_is_entity_escaped_in_node_labels(self):
        story = Story(
            name="Punctuation",
            passages=[Passage(name='"&<>|#`\\[]{}()', content="Done.")],
        )

        result = render_story_map(story)

        self.assertIn(
            '#34;#38;#60;#62;#124;#35;#96;#92;#91;#93;#123;#125;#40;#41;',
            result,
        )
        self.assertNotIn("&#", result)

    def test_punctuation_is_entity_escaped_in_choice_labels(self):
        choice = '"&<>|#`\\[{}()'
        story = Story(
            name="Punctuation choices",
            passages=[
                Passage(name="Start", content=f"[[{choice}->End]]"),
                Passage(name="End", content="Done."),
            ],
        )

        result = render_story_map(story)

        self.assertIn(
            '    p0 -->|"#34;#38;#60;#62;#124;#35;#96;#92;#91;#123;#125;#40;#41;"| p1\n',
            result,
        )

    def test_unicode_passage_and_choice_labels_are_preserved(self):
        story = Story(
            name="Unicode",
            passages=[
                Passage(name="Départ 🧭", content="[[進む café 🚀->終わり]]"),
                Passage(name="終わり", content="Done."),
            ],
        )

        result = render_story_map(story)

        self.assertIn('    p0["Départ 🧭"]\n', result)
        self.assertIn('    p0 -->|"進む café 🚀"| p1\n', result)
        self.assertIn('    p1(["終わり #40;ending#41;"])\n', result)

    def test_line_breaks_and_tabs_cannot_add_mermaid_statements(self):
        story = Story(
            name="Multiline",
            passages=[
                Passage(
                    name="First\nsecond\r\nthird\tfourth\u2028fifth",
                    content="[[Go\nforward\r\nnow\tplease\u2029thanks->End]]",
                ),
                Passage(name="End", content="Done."),
            ],
        )

        result = render_story_map(story)

        self.assertIn('    p0["First second third fourth fifth"]\n', result)
        self.assertIn('    p0 -->|"Go forward now please thanks"| p1\n', result)
        self.assertEqual(len(result.splitlines()), 4)

    def test_non_whitespace_controls_are_not_emitted_raw_in_labels(self):
        controls = "\x00\x01\x07\x1b\x7f\x80\x9f"
        story = Story(
            name="Controls",
            passages=[
                Passage(name=f"Start{controls}", content=f"[[Go{controls}->End]]"),
                Passage(name="End", content="Done."),
            ],
        )

        result = render_story_map(story)

        self.assertIsNone(re.search(r"[\x00-\x1f\x7f-\x9f]", result.replace("\n", "")))

    def test_injection_text_remains_inside_a_single_node_label(self):
        name = '\"]\nclick p0 "javascript:alert(1)"\np9["<img src=x onerror=alert(1)>`'
        story = Story(name="Injection", passages=[Passage(name=name, content="Done.")])

        result = render_story_map(story)

        self.assertEqual(len(result.splitlines()), 2)
        self.assertEqual(result.count('(["'), 1)
        self.assertEqual(result.count('"])'), 1)
        self.assertNotIn('<img', result)
        self.assertNotIn('"javascript:', result)
        self.assertNotIn("`", result)

    def test_injection_text_remains_inside_a_single_edge_label(self):
        choice = '"| p99; click p0 "javascript:alert(1)"\n%%{init: {}}%% <script>`'
        story = Story(
            name="Choice injection",
            passages=[
                Passage(name="Start", content=f"[[{choice}->End]]"),
                Passage(name="End", content="Done."),
            ],
        )

        result = render_story_map(story)

        self.assertEqual(len(result.splitlines()), 4)
        self.assertEqual(result.count(" -->"), 1)
        self.assertEqual(result.count('|"'), 1)
        self.assertEqual(result.count('"|'), 1)
        self.assertNotIn("%%{", result)
        self.assertNotIn("<script>", result)
        self.assertNotIn("`", result)

    def test_output_is_deterministic_in_story_and_link_order_without_mutation(self):
        story = Story(
            name="Stable map",
            startnode=7,
            passages=[
                Passage(
                    pid=7,
                    name="Zed",
                    content="[[Beta]] [[Alpha]] [[Beta]]",
                    tags="keep tags",
                    position="100,200",
                    size="120,90",
                ),
                Passage(pid=9, name="Alpha", content="Done."),
                Passage(pid=8, name="Beta", content="[[Zed]]"),
            ],
        )
        original = copy.deepcopy(story.model_dump())
        passage_objects = list(story.passages)

        first = render_story_map(story)
        second = render_story_map(story)

        self.assertEqual(first, second)
        self.assertEqual(story.model_dump(), original)
        self.assertTrue(all(a is b for a, b in zip(story.passages, passage_objects)))
        self.assertLess(first.index('p0["Zed"]'), first.index('p1(["Alpha'))
        self.assertLess(first.index('p1(["Alpha'), first.index('p2["Beta"]'))
        self.assertEqual(
            [line for line in first.splitlines() if " -->" in line],
            [
                '    p0 -->|"Beta"| p2',
                '    p0 -->|"Alpha"| p1',
                '    p0 -->|"Beta"| p2',
                '    p2 -->|"Zed"| p0',
            ],
        )


if __name__ == "__main__":
    unittest.main()
