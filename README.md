# Sarkari Posting – Facebook post queue

Is repo se Cloudflare Worker (`sarkari-fb-poster`) har 3 ghante Facebook page par post karta hai.

- `queue/YYYY-MM-DD.json` – us din ke posts (slot 07, 10, 13, 16, 19, 22 IST)
- `posters/YYYY-MM-DD/` – poster images
- `history.json` – pehle post ki gayi vacancies (repeat se bachne ke liye)

Queue Claude roz subah banata hai.

## v2 (28 Oct 2026 se)
- Worker har ghante 07–23 IST chalta hai (cron `30 1-17 * * *`) aur us ghante ke saare posts daalta hai.
- `type: "ca"` wale posts current affairs hain; posters `tools/make_ca_posters.py` se bante hain.
- `ca_history.json` – post ho chuke current affairs (repeat se bachne ke liye).
