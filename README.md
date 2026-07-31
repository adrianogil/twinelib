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

Install the optional Flask server dependencies with:

```sh
poetry install --extras server
```
