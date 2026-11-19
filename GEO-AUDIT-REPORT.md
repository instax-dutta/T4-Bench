# GEO Audit Report: T4-Bench

**Audit date:** 2026-11-19
**URL:** https://t4b.sdad.pro/
**Repository:** https://github.com/instax-dutta/T4-Bench
**Business type:** Research/data publisher (benchmark atlas)
**Pages analysed:** homepage + repository landing page

---

## Executive summary

Before remediation, T4-Bench was a fast static site with strong original data but almost no machine-readable surface: all numbers were rendered by JavaScript, and there was no `robots.txt`, `llms.txt`, sitemap, canonical URL, Open Graph metadata or structured data. AI crawlers could fetch the HTML but would see mostly empty containers.

**Baseline GEO Score: 33/100 (Critical).**

After the remediation described below, the site has static, crawlable benchmark tables, explicit AI-crawler permissions, `llms.txt`/`llms-full.txt`, a sitemap, canonical and social metadata, and Dataset/FAQ structured data. Projected post-fix score: **77/100 (Good)**.

### Score breakdown

| Category | Baseline | Weight | Weighted | After fixes |
|---|---:|---:|---:|---:|
| AI Citability | 45 | 25% | 11.25 | 85 |
| Brand Authority | 25 | 20% | 5.00 | 55 |
| Content E-E-A-T | 55 | 20% | 11.00 | 80 |
| Technical GEO | 30 | 15% | 4.50 | 90 |
| Schema & Structured Data | 0 | 10% | 0.00 | 85 |
| Platform Optimization | 15 | 10% | 1.50 | 65 |
| **Overall** | | | **33/100** | **77/100** |

---

## Critical issues found

1. **All primary numbers were JavaScript-rendered.** The homepage static HTML contained only about 318 words and empty containers (`#answers`, `#llm-bars`, etc.). AI crawlers that do not execute JavaScript could not read the benchmark results.
   - Fix: added a static `/benchmarks.html` page with every measured table, plus static fallback text in the homepage containers.
2. **No `llms.txt` or `llms-full.txt`.** AI agents had no concise, authoritative entry point.
   - Fix: added both files, with a curated index and a full text dump of the data.
3. **No structured data.** No Dataset, FAQ, Organization or Article markup.
   - Fix: added JSON-LD to the homepage and the static data page.
4. **No `robots.txt`.** AI crawler access was implicit rather than explicitly allowed.
   - Fix: added explicit `Allow` rules for GPTBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot and other AI crawlers.

## High priority issues

- No canonical URL, Open Graph or Twitter Card metadata.
- No sitemap.
- Repository had no description, homepage URL or topics, weakening entity discovery.
- Source credit linked to a personal blog but the site had no explicit authorship/entity block.

## Medium priority issues

- Brand "T4-Bench" is new; no third-party mentions on platforms AI models weight heavily.
- No dedicated methodology page for crawlers to quote.
- Chart labels were visual-first, not text-first.

## Low priority issues

- No favicon file (inline SVG only), though this is not a GEO blocker.
- No RSS feed; not appropriate for a static benchmark atlas.

---

## Category deep dives

### AI Citability (45 → 85)
The original data is highly citable: exact numbers, fixed hardware, named models and measured units. The failure was delivery, not content. Static tables and `llms-full.txt` now expose the same facts directly.

### Brand Authority (25 → 55)
The repository and custom domain give the project a stable identity. Source credit now points to `blog.sdad.pro`. Third-party mentions remain limited; this is the largest remaining gap.

### Content E-E-A-T (55 → 80)
Strong Experience and Expertise signals: first-hand runs on named hardware, exact software versions and original tables. Added explicit authorship/source attribution and methodology text in the README.

### Technical GEO (30 → 90)
Static files, HTTPS, fast load times and now explicit crawler access, sitemap, canonical URL and agent-readable text.

### Schema & Structured Data (0 → 85)
Added `Dataset`, `FAQPage` and `Organization` JSON-LD with name, description, creator, date and variable/measurement structure.

### Platform Optimization (15 → 65)
GitHub repository metadata now includes description, homepage and topical tags. No Wikipedia or large social presence; out of scope for this pass.

---

## Quick wins implemented

1. `llms.txt` + `llms-full.txt` for agent consumption.
2. Static `/benchmarks.html` with all tables.
3. `robots.txt` explicitly allowing AI crawlers.
4. `sitemap.xml` and canonical/social metadata.
5. GitHub repo description, homepage and topics.

## Remaining work

- Earn third-party mentions and links to improve Brand Authority.
- Add a formal license/citation file if the data is to be reused externally.
- Keep `llms-full.txt` and `benchmarks.html` regenerated whenever data changes.
