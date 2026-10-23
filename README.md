# Sarkari Posting – Facebook post queue

Is repo se Cloudflare Worker (`sarkari-fb-poster`) har 3 ghante Facebook page par post karta hai.

- `queue/YYYY-MM-DD.json` – us din ke posts (slot 07, 10, 13, 16, 19, 22 IST)
- `posters/YYYY-MM-DD/` – poster images
- `history.json` – pehle post ki gayi vacancies (repeat se bachne ke liye)

Queue Claude roz subah banata hai.
