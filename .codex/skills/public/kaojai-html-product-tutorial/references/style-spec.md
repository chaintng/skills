# KaoJai Tutorial Style Specification

Use these values as the default approved system. Adjust only when the product action requires a different placement.

## Canvas And Device

| Element | Approved value |
| --- | --- |
| Master canvas | `1080 × 1920`, `9:16` |
| Native product viewport | `390 × 844` |
| Product viewport scale | `2×` |
| Phone shell | about `832 × 1738` |
| Visible screen | about `780 × 1688` |
| Phone stage padding | about `80px 58px` |
| Phone behavior | static until splash |

The internal HTML stays native mobile size. Do not implement the product at `1080px` and shrink it.

## Social-Safe Layout

On the `1080 × 1920` master:

- Keep critical text roughly within `x: 80–930`.
- Prefer `y: 180–1380` for important copy.
- Treat the bottom `420px` as unsafe for critical text.
- Treat the far-right `150px` as risky because social action controls may cover it.
- Move the copy card when those zones conflict with the UI action.

These are starting guides, not a reason to cover the product. The action target remains the first exclusion zone.

## Typography

Use local Kanit files with weights `400`, `500`, `600`, and `700`.

| Copy role | Master-canvas size | Weight | Line height |
| --- | ---: | ---: | ---: |
| Feature eyebrow | `50px` | `600` | about `1.2` |
| Feature title | `92px` | `700` | `1.12` |
| Feature support | `58px` | `400` | `1.3` |
| Compact action card | `70px` | `600` | `1.15` |

Typography principles:

- Make tutorial copy intentionally much larger than product UI copy.
- Keep title and action copy optically balanced, not mechanically centered.
- Use tight negative tracking only for large headlines; avoid squeezing Thai body copy.
- Prefer natural line breaks. Keep compact action cards to one or two lines.
- Do not reduce type merely to keep a fixed-width card; widen or reposition the card first.

## Copy Card

Default compact card:

- dark teal: `rgba(8, 84, 77, 0.95)`
- text: `#FFFFFF`
- supporting text/border: `#CBFBF0`
- padding: about `26px 28px`
- corner radius: about `34px`
- border: `2px solid rgba(203, 251, 240, 0.74)`
- minimum height: about `116px`
- shadow: deep but soft, with no white card background

The feature-intro super may be taller, around `470px`, with about `30px 28px` padding.

Do not place an icon, rule, pulse dot, step fraction, or decorative graphic inside the card unless the brief explicitly requires it.

## Connector And Action Marker

Default connector:

- one straight `4px` teal line
- rounded ends
- thin white edge for separation
- no curve, elbow, arrowhead, or line animation

Default marker:

- `90 × 90px`
- teal center `#13BAA6`
- `15px` white ring
- outer teal halo about `21px`
- pulse from roughly `0.82` to `1.18` scale
- calm repeated pulses while the corresponding card is visible

The line begins at the card edge and terminates at the marker. The marker sits on the exact control or row being acted on.

## Motion

| Motion | Default |
| --- | --- |
| Card entrance | `0.42–0.58s`, `14–24px`, `0.97–0.99` scale |
| Card float | `-12px`, `0.68–0.85s`, one yoyo |
| Marker pulse | around `0.34–0.50s` per half-cycle, several yoyo repeats |
| Top modal | about `0.62s`, restrained back/spring ease |
| Splash banner | about `0.42s`, subtle upward settle |

Avoid continuous floating, phone-frame transitions, or decorative motion unrelated to comprehension.

## Background And Layering

- Main surrounding background: pale KaoJai teal, e.g. `#F2FDFA`.
- Ambient halos: `#CBFBF0`, heavily blurred, low opacity.
- Halos stay under the phone and product screenshot.
- Phone stays above the background.
- Callouts, connector lines, markers, and the enlarged KaoJai bug stay above the product.
- A product modal uses a translucent dark scrim while the underlying integration page remains visible.

## Product Realism

- Use official local social/provider icons.
- Use realistic avatars rather than initials when assets exist.
- Fill lists to the bottom of the visible phone screen; eight rows is a useful target for this reference layout.
- Include timestamps, previews, tags, status pills, unread counts, and provider badges when the live UI contains them.
- Match live page spacing between header, guide/banner, content grid, and cards.

## Splash

Approved reference lockup on `1080 × 1920`:

- white background
- original mascot MP4 centered, about `760 × 1351`, `top: 40px`
- official primary banner about `720 × 240`, `top: 980px`
- mascot and banner read as one close lockup in the upper half
- no phone frame behind the splash

Treat these coordinates as a strong starting point; inspect multiple mascot frames because the visible mascot bounds change during the dance.

