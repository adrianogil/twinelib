import os
from .models import Story, Passage

def load_template() -> str:
    """
    Load the template file from the templates directory.
    """
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, "templates", "twine_story.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def render_passages(story: Story) -> str:
    """
    Render all passages into HTML.
    """
    passage_strs = []
    for passage in story.passages:
        # Build attributes string; include position and size only if present.
        attrs = f'pid="{passage.pid}" name="{passage.name}" tags="{passage.tags}"'
        if passage.position:
            attrs += f' position="{passage.position}"'
        if passage.size:
            attrs += f' size="{passage.size}"'
        passage_html = f'        <tw-passagedata {attrs}>{passage.content}</tw-passagedata>'
        passage_strs.append(passage_html)
    return "\n".join(passage_strs)

def render_story_data(story: Story) -> str:
    """
    Build the <tw-storydata> block using the story properties and passages.
    """
    # In this simple example, many fields are given default values.
    hidden_attr = ' hidden' if getattr(story, "hidden", None) else ''
    passages_html = render_passages(story)
    storydata_html = (
        f'<tw-storydata name="{story.name}" startnode="{story.startnode}" '
        f'creator="Twine" creator-version="2.10.0" '
        f'format="Harlowe" format-version="3.3.9" '
        f'ifid="" options="debug" tags="" zoom="1"{hidden_attr}>\n'
        f'    <style role="stylesheet" id="twine-user-stylesheet" type="text/twine-css"></style>\n'
        f'    <script role="script" id="twine-user-script" type="text/twine-javascript"></script>\n'
        f'{passages_html}\n'
        f'</tw-storydata>'
    )
    return storydata_html

def render_story(story: Story) -> str:
    """
    Load the HTML template from file and replace the two placeholders:
      - {{TWINE_STORY_NAME}} with story.name
      - {{TWINE_STORY_DATA}} with the rendered storydata block.
    """
    template = load_template()
    story_data_html = render_story_data(story)
    html = template.replace("{{TWINE_STORY_NAME}}", story.name) \
                   .replace("{{TWINE_STORY_DATA}}", story_data_html)
    return html

def story_from_dict(data: dict) -> Story:
    """
    Create a Story instance from a dictionary.

    Expected dictionary format:
    {
        "story_name": "Dragon Story",
        "passages": [
            {
                "name": "Start",
                "content": [
                    "Some text.",
                    "More text.",
                    {"choices": {"Choice 1": "Target1", "Choice 2": "Target2"}}
                ]
            },
            ...
        ]
    }
    """
    story_name = data.get("story_name")
    passages_data = data.get("passages", [])
    passages = []
    pid_counter = 1
    for p in passages_data:
        p["pid"] = pid_counter
        pid_counter += 1
        passage = Passage(**p)
        passages.append(passage)
    return Story(name=story_name, passages=passages)

__all__ = ["Story", "Passage", "render_story", "story_from_dict"]
