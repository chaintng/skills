# Tutorial QA Checklist

## Product Fidelity

- [ ] The owning live page and source component were inspected.
- [ ] Product footage is HTML-first; any MP4 usage has a clear reason.
- [ ] Remote assets were localized before render.
- [ ] The internal UI is truly `390 × 844`, not a desktop canvas scaled down.
- [ ] Icons, avatars, colors, copy, and state transitions match the real product.
- [ ] Lists/cards fill the phone naturally without obvious empty mock space.

## Copy And Safe Areas

- [ ] Kanit is loaded locally and used for every tutorial annotation.
- [ ] Feature eyebrow/title/support and compact callouts follow the approved size hierarchy.
- [ ] Every card explains one action or benefit in one or two lines.
- [ ] No critical copy sits in the lower social description/comment zone.
- [ ] No copy covers the action it describes.
- [ ] Copy position changes when a different action needs space.
- [ ] Provider names are omitted from generic instructional copy when the icon/UI already makes the context clear.

## Lines And Markers

- [ ] One straight line connects each visible card to its target.
- [ ] The marker is on the actual action area.
- [ ] The marker pulse is calm, repeated, and slower than a tap flash.
- [ ] No pulsing dot or decorative line remains inside the card.
- [ ] Marker, line, and card stay above the product screenshot.

## Motion And Scenes

- [ ] Phone frame remains static until the splash.
- [ ] Product actions play continuously and remain understandable.
- [ ] Modals slide from the correct direction while retaining the dimmed page behind them.
- [ ] No infinite animation, random timing, or render-time network state exists.
- [ ] Splash uses the original mascot, official banner, tight spacing, and upper positioning.
- [ ] Audio is absent unless requested; narration and SFX are not added automatically.

## Verification

- [ ] Snapshot the first feature super.
- [ ] Snapshot every meaningful click/filter/modal/list state.
- [ ] Snapshot at least three mascot positions during the splash.
- [ ] Inspect the full `1080 × 1920` composition, not only cropped phone UI.
- [ ] Run HyperFrames lint/check and record runtime, layout, motion, and contrast results.
- [ ] Distinguish foreground readability problems from contrast warnings caused by intentionally dimmed/covered background UI.
- [ ] Confirm preview and Studio URLs return successfully.
- [ ] Do not render/export unless explicitly requested.

