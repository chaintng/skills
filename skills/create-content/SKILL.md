---
name: create-content
description: Create researched content notes under a content root using the Personal/my-contents/{YYYY}/{CONTENT-TITLE}/ pattern with index.md as the main note and a local attachments/ folder for transcript and graphics. Use when the user wants Codex to create a new reel/blog/news content, research a specified topic, draft Thai storytelling content, generate or attach a transcript, find and download related graphics, or normalize an existing my-contents note to this structure.
---

# Create Content

Create new content using the `Personal/my-contents/{YYYY}/{CONTENT-TITLE}/index.md` pattern.
Expect `CONTENT_ROOT` to point at the root directory that contains `Personal/my-contents`.

## Content Contract

Use this content root:

```text
$CONTENT_ROOT/Personal/my-contents
```

For a new content item, create:

```text
Personal/my-contents/{YYYY}/{CONTENT-TITLE}/
├── index.md
└── attachments/
```

Put all content-local assets inside that content folder's `attachments/` directory:
- transcript files such as `.srt`
- downloaded graphics and illustrations
- screenshots and charts
- generated cover or insert images if requested

Do not place new content assets in the year-level `attachments/` folder when a content-specific folder exists.

## First Step

Infer the content name from the user's input, topic, or requested angle whenever a reasonable folder name can be derived.

Ask for the content name only when the request is too ambiguous to infer a stable title.

From the provided or inferred title:
- derive `{CONTENT-TITLE}` as a folder-safe slug
- use the current year for `{YYYY}` unless the user specifies another year
- create the folder before drafting so all downloaded assets land in the final location

## Workflow

1. Inspect nearby examples in `Personal/my-contents/{YYYY}/...` when the structure or tone is unclear.
2. Research the user-specified topic using current, source-backed information.
3. Prefer the original source first for factual claims. Use secondary coverage only to clarify or triangulate.
4. Create or update `attachments/` with the transcript and downloaded graphics.
5. Write `index.md` in the established house style.
6. Re-read the generated note and verify every embedded filename exists in the local `attachments/` folder.

## Research Rules

For current topics, verify facts live before writing.

Prefer sources in this order:
1. original blog post, paper, press release, dataset, or official page
2. primary reporting that quotes the original source accurately
3. other coverage only when needed for context

When summarizing facts:
- keep exact dates when they matter
- distinguish source-backed facts from your interpretation
- do not import dramatic claims from secondary articles if the original source does not support them

## Graphics Rules

Find graphics that are directly related to the topic.

Prefer:
- official charts and figures from the original source
- screenshots or diagrams from the primary source page
- related official illustrations, event posters, product images, or reference images when they materially help the story

Save every file into the content-local `attachments/` directory.

In `index.md`, embed graphics with filename wikilinks using the filename only:

```md
![[cumulative-crimes.webp]]
![[governance-consensus.png]]
```

If a graphic supports a specific section, place it next to that section instead of dumping all graphics at the top.

## Transcript Rules

Generate a transcript file in Thai unless the user asks for another language.

Default transcript path:

```text
Personal/my-contents/{YYYY}/{CONTENT-TITLE}/attachments/<transcript-name>.srt
```

Link the transcript from `index.md` with a filename wikilink using the filename only:

```md
## Transcript
- [[emergence-ai-ai-society.srt]]
```

If the user already has a final video or an existing SRT, reuse it instead of regenerating from scratch.

## index.md Contract

Follow the current pattern used in the content root. Start from the real examples in `references/content-layout.md`.

Use this frontmatter shape unless the user needs something else:
- `references:`
- `tags:`
- `favourite: false`
- `created:`
- `modified:`
- `template: "[[General]]"`
- `draft:`
- `title:`
- `published:` when known
- `published-url:` when known
- `filename:` matching the folder slug when the note already uses it

Default body structure for researched short-form content:
- `# <Title>`
- `## Caption`
- `## Hook`
- `## Content`
- topic-specific sub-sections as needed
- `## Closing`
- `## Transcript`
- `# References`

Keep the tone aligned with the user's existing note patterns:
- concise
- spoken-language friendly
- story-first
- can be scary, funny, nerdy, or character-driven depending on the topic and nearby examples

## Example Usage

Use `Personal/my-contents/2026/emergece-world-ai-experiments/index.md` as the reference example for:
- researched news content
- embedded official charts
- transcript stored in local `attachments/`
- section order for a reel/news explainer

If the user asks for a different style, inspect another nearby example first and adapt.

## Final Check

Before finishing:
- confirm the folder path is correct
- confirm `index.md` exists
- confirm every linked graphic exists in local `attachments/`
- confirm the transcript file exists and is linked from `index.md`
- confirm any factual claims that depend on current news were verified from current sources
