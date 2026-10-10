# twinelib
Python Library to parse and generate twine stories

Before rendering, twinelib validates Twine passage links and raises an error when
content links to a missing passage.

Compute a story graph report with `compute_story_stats`. The report counts
passages and links, and lists dead-end and unreachable passages:

```python
from twinelib import compute_story_stats, story_from_dict

story = story_from_dict(data)
stats = compute_story_stats(story)

print(stats.passage_count)
print(stats.link_count)
print(stats.dead_end_passages)
print(stats.unreachable_passages)
```

By default, reachability starts at the passage identified by the story's
`startnode` PID. Pass `start_passage="Passage name"` to analyze from a specific
passage. Broken links raise the same validation error used during rendering.

## Export a Mermaid story map

`render_story_map` returns Mermaid source showing every passage and choice.
Endings (passages without outgoing links) have rounded nodes and an `ending`
label. Unreachable passages have a dashed red outline and an `unreachable`
label, including unreachable endings.

```python
from pathlib import Path
from twinelib import render_story_map, story_from_dict

story = story_from_dict({
    "story_name": "Forest paths",
    "passages": [
        {"name": "Start", "content": "[[Enter the forest->Forest]] [[Go home->Home]]"},
        {"name": "Forest", "content": "[[Home<-Follow the trail]]"},
        {"name": "Home", "content": "The end."},
        {"name": "Hidden clearing", "content": "An undiscovered ending."},
    ],
})

mermaid = render_story_map(story, direction="LR")
Path("story-map.mmd").write_text(mermaid, encoding="utf-8")
# For GitHub or another Markdown viewer with Mermaid support:
Path("story-map.md").write_text("```mermaid\n" + mermaid + "```\n", encoding="utf-8")
```

Open the Markdown file in a Mermaid-enabled viewer or use a Mermaid renderer
with the `.mmd` file. Exporting needs no extra dependencies or Graphviz;
rendering the diagram requires Mermaid support in your viewer.

- `direction` defaults to `"TD"`; `"TB"`, `"BT"`, `"LR"`, and `"RL"` are also accepted.
- `start_passage="Forest"` overrides the reachability start. Otherwise, the
  story's `startnode` PID is used, falling back to the first passage only when
  all passage IDs are absent, just like `compute_story_stats`.
- Choices use `[[Target]]`, `[[Label->Target]]`, or `[[Target<-Label]]`.
  Repeated choices and loops are preserved. Empty choice labels produce
  unlabeled arrows. Labels are escaped and whitespace is collapsed to spaces;
  non-whitespace control characters are replaced with `�`.
- Broken links, duplicate passage names, and invalid starts raise `ValueError`.
  An empty story exports an empty flowchart.
- This is static link analysis: Twine macros, variables, and conditions are
  not executed. An `ending` means no parsed outgoing links, not a narrative
  ending tag or proof that gameplay can reach it.

Run the tests with `python -m unittest discover -s tests -v`.

Install the optional Flask server dependencies with:

```sh
poetry install --extras server
```
