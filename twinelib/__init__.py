import os
import re
from html import escape
from typing import Optional

from .models import Passage, Story, StoryStats

TWINE_LINK_PATTERN = re.compile(r"\[\[([^\]]*)\]\]")


def _escape_attribute(value) -> str:
    return escape(str(value), quote=True)


def extract_link_target(link_text: str) -> str:
    """
    Extract the target passage name from a Twine link body.

    Supports the common Twine forms:
      - [[Target]]
      - [[Display text->Target]]
      - [[Target<-Display text]]
    """
    if "->" in link_text:
        return link_text.split("->", 1)[1].strip()
    if "<-" in link_text:
        return link_text.split("<-", 1)[0].strip()
    return link_text.strip()


def iter_passage_links(content: str):
    """
    Yield target passage names linked from a passage's Twine markup.
    """
    for match in TWINE_LINK_PATTERN.finditer(content):
        yield extract_link_target(match.group(1))


def validate_story_links(story: Story) -> None:
    """
    Validate that all Twine links point to existing passage names.
    """
    passage_names = [passage.name for passage in story.passages]
    duplicate_names = sorted({name for name in passage_names if passage_names.count(name) > 1})
    if duplicate_names:
        raise ValueError(f"Duplicate passage names found: {', '.join(duplicate_names)}")

    passage_name_set = set(passage_names)
    missing_links = []

    for passage in story.passages:
        for target in iter_passage_links(passage.content):
            if not target:
                missing_links.append((passage.name, target))
            elif target not in passage_name_set:
                missing_links.append((passage.name, target))

    if missing_links:
        formatted_links = ", ".join(
            f"{source!r} -> {target!r}" for source, target in missing_links
        )
        raise ValueError(f"Story contains links to missing passages: {formatted_links}")


def compute_story_stats(
    story: Story, start_passage: Optional[str] = None
) -> StoryStats:
    """
    Compute passage and link statistics for a valid story graph.

    When ``start_passage`` is omitted, the passage whose ``pid`` matches the
    story's ``startnode`` is used. Stories constructed without passage IDs use
    their first passage as the start.
    """
    validate_story_links(story)

    links_by_passage = {
        passage.name: list(iter_passage_links(passage.content))
        for passage in story.passages
    }

    if not story.passages:
        if start_passage is not None:
            raise ValueError(f"Start passage not found: {start_passage!r}")
        return StoryStats(
            passage_count=0,
            link_count=0,
            dead_end_passages=[],
            unreachable_passages=[],
        )

    if start_passage is None:
        matching_start_passages = [
            passage.name
            for passage in story.passages
            if passage.pid == story.startnode
        ]
        if matching_start_passages:
            start_passage = matching_start_passages[0]
        elif all(passage.pid is None for passage in story.passages):
            start_passage = story.passages[0].name
        else:
            raise ValueError(
                f"No passage has the story startnode pid: {story.startnode!r}"
            )
    elif start_passage not in links_by_passage:
        raise ValueError(f"Start passage not found: {start_passage!r}")

    reachable = set()
    pending = [start_passage]
    while pending:
        passage_name = pending.pop()
        if passage_name in reachable:
            continue
        reachable.add(passage_name)
        pending.extend(links_by_passage[passage_name])

    return StoryStats(
        passage_count=len(story.passages),
        link_count=sum(len(targets) for targets in links_by_passage.values()),
        dead_end_passages=[
            passage.name
            for passage in story.passages
            if not links_by_passage[passage.name]
        ],
        unreachable_passages=[
            passage.name
            for passage in story.passages
            if passage.name not in reachable
        ],
    )

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
        attrs = (
            f'pid="{_escape_attribute(passage.pid)}" '
            f'name="{_escape_attribute(passage.name)}" '
            f'tags="{_escape_attribute(passage.tags)}"'
        )
        if passage.position:
            attrs += f' position="{_escape_attribute(passage.position)}"'
        if passage.size:
            attrs += f' size="{_escape_attribute(passage.size)}"'
        passage_html = f'        <tw-passagedata {attrs}>{passage.content}</tw-passagedata>'
        passage_strs.append(passage_html)
    return "\n".join(passage_strs)

def render_story_data(story: Story) -> str:
    """
    Build the <tw-storydata> block using the story properties and passages.
    """
    # In this simple example, many fields are given default values.
    validate_story_links(story)
    hidden_attr = ' hidden' if getattr(story, "hidden", None) else ''
    passages_html = render_passages(story)
    storydata_html = (
        f'<tw-storydata name="{_escape_attribute(story.name)}" '
        f'startnode="{_escape_attribute(story.startnode)}" '
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
    html = template.replace("{{TWINE_STORY_NAME}}", escape(story.name)) \
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
        passage_data = p.copy()
        passage_data["pid"] = pid_counter
        pid_counter += 1
        passage = Passage(**passage_data)
        passages.append(passage)
    return Story(name=story_name, passages=passages)

__all__ = [
    "Story",
    "Passage",
    "StoryStats",
    "compute_story_stats",
    "extract_link_target",
    "iter_passage_links",
    "render_story",
    "story_from_dict",
    "validate_story_links",
]
