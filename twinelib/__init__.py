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
    Render all the passages from the story into HTML.
    """
    passage_strs = []
    for passage in story.passages:
        passage_html = (
            f'        <tw-passagedata pid="{passage.pid}" '
            f'name="{passage.name}" '
            f'tags="{passage.tags}" '
            f'position="{passage.position}" '
            f'size="{passage.size}">'
            f'{passage.content}'
            f'</tw-passagedata>'
        )
        passage_strs.append(passage_html)
    return "\n".join(passage_strs)

def render_story_data(story: Story) -> str:
    """
    Build the <tw-storydata> block using the story properties and passages.
    """
    hidden_attr = ' hidden' if story.hidden else ''
    passages_html = render_passages(story)
    storydata_html = (
        f'<tw-storydata name="{story.name}" startnode="{story.startnode}" '
        f'creator="{story.creator}" creator-version="{story.creator_version}" '
        f'format="{story.format}" format-version="{story.format_version}" '
        f'ifid="{story.ifid or ""}" options="{story.options}" tags="{story.tags}" '
        f'zoom="{story.zoom}"{hidden_attr}>\n'
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
      - {{TWINE_STORY_DATA}} with the storydata block (including passages)
    """
    template = load_template()
    story_data_html = render_story_data(story)
    # Replace only the two placeholders in the template:
    html = template.replace("{{TWINE_STORY_NAME}}", story.name) \
                   .replace("{{TWINE_STORY_DATA}}", story_data_html)
    return html

__all__ = ["Story", "Passage", "render_story"]
