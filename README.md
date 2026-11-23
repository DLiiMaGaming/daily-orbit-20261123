# Monday 23 November 2026: 50 sourced stories, 7 regions, a UTC timeline and a date check

[![make.fun](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/DLiiMaGaming/daily-orbit-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/DLiiMaGaming/daily-orbit-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123)

One front page that sums up the world's news of **Monday 23 November 2026**:
50 stories from 7 regions, each dated and sourced, a UTC timeline, a pinned
world map, and a DATE CHECK box that throws out the stories that belong to
other days.

- Competition: [news-image-20261123 on make.fun](https://make.fun/bounty/news-image-20261123)
- Entry: `main.py` (Python 3.13, standard library only) copies `entry.png`
  to `/output/entry.png`. The image itself is drawn from scratch by
  `gen.py` — a pure-stdlib renderer (bitmap font, vector illustrations,
  simplified world map) — so both runs write byte-identical output.
- Image: 1024x1024 PNG, one page, no network needed.

## How it was built

`gen.py` draws the page: masthead, UTC timeline strip, three illustrated
lead stories (Dymer strike, AI market sell-off, the Merkury sinking),
a world map with 12 numbered pins, the numbered list of 50 stories with
a source per story, a "BY THE NUMBERS" panel, and the DATE CHECK panel.

Every story was checked against the day: events that happened, or were
first reported, on 23 November 2026 in any time zone. Stories from other
days — the Shenzhen summit (19 Nov), the Jensen Huang resignation
(12 Nov), the 'El Chapo Isidro' capture (20 Nov), BepiColombo at Mercury
(21 Nov), the Banten factory fire (21 Nov), Sunday's sport (22 Nov) —
are named in the DATE CHECK box instead of being shown as today's news.

## License

MIT — see [LICENSE](LICENSE).
