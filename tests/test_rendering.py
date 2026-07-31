import unittest

from twinelib import Passage, Story, render_story


class StoryRenderingTest(unittest.TestCase):
    def test_render_story_escapes_dynamic_attributes_and_title(self):
        story = Story(
            name='A "quoted" & <story>',
            passages=[
                Passage(
                    pid=1,
                    name='Start "here" & <now>',
                    tags='one "two" & <three>',
                    position='10,"20" & <30>',
                    size='100 "x" & <50>',
                    content="The end.",
                )
            ],
        )

        rendered = render_story(story)

        self.assertIn("<title>A &quot;quoted&quot; &amp; &lt;story&gt;</title>", rendered)
        self.assertIn(
            'name="A &quot;quoted&quot; &amp; &lt;story&gt;"', rendered
        )
        self.assertIn(
            'name="Start &quot;here&quot; &amp; &lt;now&gt;"', rendered
        )
        self.assertIn('tags="one &quot;two&quot; &amp; &lt;three&gt;"', rendered)
        self.assertIn('position="10,&quot;20&quot; &amp; &lt;30&gt;"', rendered)
        self.assertIn('size="100 &quot;x&quot; &amp; &lt;50&gt;"', rendered)

    def test_render_story_preserves_twine_markup_in_passage_content(self):
        content = '(if: $score < 2)[Try [[Again->Start]]].'
        story = Story(
            name="Markup",
            passages=[Passage(pid=1, name="Start", content=content)],
        )

        rendered = render_story(story)

        self.assertIn(f'>{content}</tw-passagedata>', rendered)


if __name__ == "__main__":
    unittest.main()
