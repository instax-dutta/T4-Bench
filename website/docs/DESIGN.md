# Design direction: Field instrument logbook

## Category and first screen
This is a benchmark data atlas, not a product landing page. The visitor arrives
to answer one task-based question: which model should they run for chat, agents,
fine-tuning, images or video on this exact 2x T4 machine?
The first screen therefore shows the headline answers, the machine and the
three metric scales; it does not open with a slogan or a feature list.

## Direction card
- **North star:** reading the site should feel like opening a carefully kept
  instrument logbook: measurements first, conclusions pinned to evidence.
- **Tone:** calm (low saturation), precise (strict 8px grid), dense but legible
  (tables and charts visible without scrolling), substantial (heavy numerals,
  thin rules), serious (no decorative gradients or glow).
- **Reference and decisions:** benchmark reports from ML benchmarking writeups
  use dark dashboards and neon accents. That does not suit a document people
  should read carefully. We keep the baseline: a results table, a metric chart
  and footnotes. We keep the precision of an instrument panel but replace the neon glow with
  flat dark fields, hairline rules and one signal colour, because the content is a measured record, not a product demo.
- **Generation engine:** a laboratory notebook and an analogue chart recorder:
  ruled paper, tabular numbers, one red annotation pen.
- **First-screen skeleton:** a compact masthead, a two-column lead (question +
  four answer cards), then task-based sections. Each section uses the same
  grammar: one plain-language bar chart, one table, one short verdict, and an
  animated diagram in a web component.
- **Page structure:** masthead -> verdict strip -> image section -> video
  section -> H3 memory-wall section -> method and caveats -> sources.
- **Typography:** system UI stack for prose, monospace stack for every number
  and label. Display numerals 56-72px; body 15-17px; chart labels 12-13px.
- **Colour:** dark field `#0E1110`, light ink `#ECEDE6`, muted `#9AA19A`, rule `#2C322E`,
  signal vermilion `#FF6B4A`, time teal `#4FD1C5`, safe green `#67C77D`.
- **Primary visual:** familiar horizontal bar charts only, repeated across every
  campaign. Eight ManimGX diagrams animate the same data and are wrapped in an
  `<mx-clip>` web component with poster, lazy playback and replay. No scatter
  plots or specialist diagnostics are shown to the public.
- **Iconography:** no icon set. Numbers, section indices and rules do the work.
- **Control grammar:** squared-off 2px-rule sections, 4px radius on small tags,
  selected state is a filled vermilion tab with moving underline.
- **Motion:** three basic animations - (1) hero metric bars grow once on entry;
  (2) metric tabs move one shared underline; (3) chart clips play once when
  scrolled into view and pause offscreen. No parallax, no cursor effects.
- **Memorable moment:** the image-model bar race where FLUX pulls ahead while
  the number ticks to 374 images/hour; the paper annotation lands last.
- **What we gave up:** dark gradient dashboard, glow, floating cards, icon
  library, web fonts, charts JS library, client-side build step, scatter plots,
  CLIP jargon in the interface, and animation credits.

## Alternatives considered
| Direction | Why not |
|---|---|
| Dark GPU dashboard, neon accents | Familiar but reads as marketing; the data should read as a record. |
| Editorial magazine with large photography | No photographs are part of the evidence; images would be decoration. |
| Minimal monochrome table only | Accurate but hides the comparative story the user asked to visualise. |

## Delivery constraint
Static HTML + CSS + vanilla JS, no package manager at runtime. All animation
is pre-rendered with ManimGX and compressed to WebM/MP4 with posters, so the
site works offline and stays small.
