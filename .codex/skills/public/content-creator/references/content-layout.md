# Content Layout Reference

Use this content path:

```text
$CONTENT_ROOT/Personal/my-contents
```

Expect `CONTENT_ROOT` to be set to the root directory that contains `Personal/my-contents`.

## Folder Layout

Create each new content item here:

```text
Personal/my-contents/{YYYY}/{CONTENT-TITLE}/
├── index.md
└── attachments/
```

Put all local assets under that content folder's `attachments/` directory.

## index.md Frontmatter Pattern

Use the current content pattern as the baseline:

```yaml
---
references:
tags:
  - reels
  - hot
favourite: false
created: 2026-05-30T14:30:00+07:00
modified: 2026-05-30T17:49:33+07:00
template: "[[General]]"
draft: false
title: Example Title
published: 2026-05-30T13:00:00
published-url: https://www.instagram.com/reel/...
filename: example-title
---
```

Keep `published`, `published-url`, and `filename` only when they are known or already part of the note's pattern.

## index.md Body Pattern

For researched reel/news content, use this structure:

```md
# <Title>

## Caption
...

## Hook
- ...

## Content
- ...

## <topic subsection>
- ...

## Closing
- ...

## Transcript
- [[transcript-file.srt]]

# References
- <source>
```

Embed local graphics with filename wikilinks using the filename only:

```md
![[cumulative-crimes.webp]]
![[governance-consensus.png]]
```

## Example: Emergence World Content

Reference example:

```text
Personal/my-contents/2026/emergece-world-ai-experiments/index.md
```

Reference attachments:

```text
Personal/my-contents/2026/emergece-world-ai-experiments/attachments/
├── cumulative-crimes.webp
├── governance-consensus.png
├── five-worlds-five-outcomes.webp
└── emergence-ai-ai-society.srt
```

What this example demonstrates:
- current-news research grounded in an original source
- graphics saved under content-local `attachments/`
- inline chart placement near the matching argument
- transcript linked from `## Transcript`
- a note that reads like spoken Thai storytelling rather than a formal article
