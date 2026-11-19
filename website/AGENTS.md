## Purpose
Static benchmark visualisation site: all measured data, rendered with lightweight HTML/CSS/JS and ManimGX clips.

## Ownership
- `index.html`, `styles.css`, `app.js`, `data.js` - the site
- `assets/**` - compressed clips and posters
- `manim/scenes.py` - animation source
- `scripts/build_data.py` - data generator
- `docs/DESIGN.md` - visual direction card
- `README.md` - build and open instructions

## Local Contracts
- Never hand-edit numbers into the HTML; regenerate `data.js` from the unified benchmark files.
- No runtime dependencies, web fonts or chart libraries.
- Clips must have a poster and must not autoplay offscreen.
- Every chart has an equivalent table.

## Work Guidance
- Keep the dark-field/hairline/monospace palette and numerals; avoid gradients and glow.
- Re-run the oil-ui screenshot tool after visual changes and keep evidence in the task directory.

## Verification
- `node --check app.js`
- `python3 scripts/build_data.py`
- `node ../scripts/verify-dox.mjs ..` from the unified root.
- `node /Users/saiduttaabhishekdash/.agents/skills/oil-ui/scripts/shoot.mjs index.html --size 1280x900,390x844 --full`

## Child DOX Index
- `website/docs/AGENTS.md` - design direction and visual evidence
