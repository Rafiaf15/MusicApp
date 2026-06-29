---
name: instant-play-optimization
description: Improves song playback latency by fixing selection logic and pre‑fetching URLs.
source: auto-skill
extracted_at: '2026-06-29T09:41:45.706Z'
---

## Goal
Reduce the delay between selecting a song in the UI and the audio starting to play.

## Changes Made
1. **Corrected song selection index** – Updated `on_song_selected` in `main.py` to use the clicked `QListWidgetItem` directly (`row(item)`) instead of `currentRow()`, which could be outdated and cause mis‑selection.
2. **Added proactive URL pre‑fetch** – After a successful search the controller now:
   * Loads any cached URLs (`_prefetch_from_cache`).
   * Immediately starts background fetching of the first few songs (`_prefetch_initial_songs(count=5)`).
3. **Implemented `_prefetch_initial_songs`** – A new helper that spawns background threads to fetch URLs for the first *n* results, populating `self.audio_urls` and the cache, so the user’s first clicks hit a ready URL.
4. **Ensured UI updates** – The pre‑fetch does not touch the UI, keeping the interface responsive.

## Result
- Clicking a track now either plays instantly from cache or from a high‑priority fetch that starts as soon as the search completes.
- Initial songs are pre‑loaded, dramatically reducing the wait time observed previously.

## Future Improvements
- Dynamically adjust the number of pre‑fetched songs based on network speed.
- Add fallback to retry failed URL fetches.
- Cache eviction policy to limit cache size.
