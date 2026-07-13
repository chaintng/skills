---
name: kaojai-html-product-tutorial
description: Create or revise KaoJai.ai product tutorial, walkthrough, feature-demo, Reels, TikTok, Shorts, or phone-framed HyperFrames videos. Use this skill whenever a KaoJai product flow should be demonstrated on screen, especially when choosing between HTML and MP4 footage, reconstructing admin or landing-page UI, adding Thai instructional copy, action markers, connector lines, an iPhone frame, or a branded splash. Prefer this skill even when the user only says “make a tutorial”, “show this feature”, “turn the demo into video”, or asks to preserve the established KaoJai tutorial style.
compatibility: HyperFrames HTML composition, local KaoJai source/assets, browser or source inspection, Kanit font files
---

# KaoJai HTML Product Tutorial

Create a product-realistic tutorial that stays readable inside a short-form social feed. The product UI is the evidence; annotations explain it without covering the action.

Read [references/style-spec.md](references/style-spec.md) before designing or changing the visual system. Read [references/qa-checklist.md](references/qa-checklist.md) before handoff.

## Core Direction

- Build the product footage in HTML whenever the product exists as a web UI. HTML keeps text, icons, states, and motion sharp at export resolution.
- Use MP4 only for material that needs real recorded motion or cannot be reconstructed faithfully, such as mascot footage, camera footage, or an intentional supplied clip.
- Reconstruct from the real KaoJai source and live product. Do not invent a generic SaaS interface when the real component, copy, icon, avatar, spacing, or interaction is available.
- Keep the phone frame static from the first product frame until the splash replaces it. Do not animate the iPhone in or out.
- Use a `1080 × 1920` master composition. Build the product UI at a native `390 × 844` viewport and scale it `2×` inside the phone screen.
- Default to no narration. Add music only when requested; never generate voice or sound effects by default.

## Source Order

Use this order before authoring the mock:

1. Inspect the current live page or authenticated product state.
2. Find the owning component and styles in `/Users/chaintng/Projects/kaojai-ai`.
3. Reuse official local logos, channel icons, mascot media, avatars, colors, copy, and font files.
4. Recreate the exact state changes as deterministic HTML/GSAP.
5. Use screenshots only as a visual reference, not as the main product footage, unless source reconstruction is impossible.

Localize remote assets into the tutorial project before rendering. A render must not depend on live network requests.

## Tutorial Structure

For each feature:

1. Show a clear feature super during its first seconds.
2. Let the UI action play without cutting away.
3. Replace the super with short action copy as the flow progresses.
4. Put a pulse marker on the exact action target.
5. Draw one straight connector from the copy card toward the marker.
6. Move the copy card for each action instead of pinning every card to one location.
7. End with the approved KaoJai splash after the phone disappears.

Use one continuous flow when the feature is easy to understand sequentially. Do not add scene cuts merely to create motion.

## HTML Product Footage

- Match real layout density. Populate lists, chats, cards, timestamps, tags, unread counts, and avatars until the native phone screen looks complete.
- Use actual provider icons and recognizable local avatar assets. Avoid empty generic placeholders.
- Preserve realistic scroll and clipping behavior inside `390 × 844`.
- Keep UI copy at native mobile sizes. Scaling the true mobile viewport creates readable text; building the UI directly at `1080px` makes it look like a shrunk desktop page.
- Match live interaction patterns. Example: a connect flow should use a top-sliding modal with a translucent scrim while the integration page remains visible behind it.
- Keep spacing deliberate: separate header, informational banner, content grid, and cards; do not compress them into one dense block.

## Annotation Copy

- Write Thai-first, short, spoken-language copy that explains one outcome or action.
- Prefer generic user language over provider names when the provider is already visually obvious.
- Do not describe every click. Explain the important change in the user’s mental model.
- Keep compact action cards to one or two lines.
- Use the first super hierarchy: `ฟีเจอร์` eyebrow, benefit-led title, one supporting sentence.
- Do not put decorative graphics, horizontal rules, or pulsing dots inside the copy card.
- Do not force every copy card to the same width or position. Size it for the message and available safe area.

## Placement Rules

Treat social overlays and the product action as hard exclusion zones.

- Keep critical copy away from the lower Reels/TikTok description and comment area.
- Avoid the far-right interaction rail and the very top app chrome.
- Never cover the control, selection, modal content, filter, or row being explained.
- Place the card near the action, then use a straight line to bridge the remaining distance.
- Put the pulse marker on the action target, not inside the copy card.
- Reposition annotations per step. Readability wins over visual consistency of location.
- Keep the annotation above the phone screenshot when layers overlap; keep background halos below both.

## Motion Rules

- Keep motion small, elegant, and seek-safe.
- Enter cards over roughly `0.42–0.58s` with a subtle `14–24px` offset and slight scale.
- Float the visible card about `12px` upward and back once using `sine.inOut`; do not bob continuously.
- Pulse the action marker several times at a calm cadence. Keep the connector straight and still.
- Use a top slide of about `0.62s` for product modals; retain the dimmed page behind the sheet.
- Do not fade or scale the phone frame between product states.
- Keep every GSAP timeline paused and deterministic. Avoid infinite repeats, clocks, random values, and network-dependent state.

## Brand And Splash

- Use Kanit from local font files for all tutorial copy.
- Use KaoJai teal `#11BAA6`, dark annotation teal, and pale teal background halos.
- Avoid a plain white surrounding background while the light phone UI is visible; it blends into the device.
- The ending splash may use white because the phone is gone.
- Use the original mascot video, not a generated cutout, unless explicitly requested.
- Keep the mascot and official banner close as one lockup and position the whole lockup in the upper half of the splash.

## Delivery Workflow

1. Confirm the feature flow and inspect its real owner surface.
2. Build or update the HTML product state at `390 × 844`.
3. Add the static phone, background, feature super, action cards, connectors, and markers.
4. Snapshot the beginning, each action state, modal state, filters/lists, and splash.
5. Run HyperFrames lint/check and inspect runtime, layout, motion, and visual contrast findings.
6. Keep Studio and preview URLs running for review.
7. Do not render/export unless the user asks; they may export from Studio themselves.

Use the approved reference project for concrete implementation patterns:

`/Users/chaintng/Projects/my-projects/vdo-content/hyperframe-projects/kaojai-autoplay-demo`

