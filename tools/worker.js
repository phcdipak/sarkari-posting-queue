// ============================================================
//  Sarkari Posting – Facebook Auto Poster (Cloudflare Worker)
//  Har 3 ghante (7, 10, 1, 4, 7, 10 baje IST) GitHub queue se
//  aaj ka poster uthakar Facebook Page par post karta hai.
// ------------------------------------------------------------
//  Cloudflare Settings → Variables and Secrets:
//    QUEUE_BASE    (Text)   https://raw.githubusercontent.com/<USERNAME>/sarkari-posting-queue/main
//    FB_PAGE_ID    (Secret) aapke page ka ID
//    FB_PAGE_TOKEN (Secret) Page Access Token
//    TEST_KEY      (Secret) koi bhi password, manual test ke liye
//    GRAPH_VERSION (Text, optional) default v26.0
//  Cloudflare Settings → Triggers → Cron:  30 1,4,7,10,13,16 * * *
// ============================================================

const SLOTS = ["07", "10", "13", "16", "19", "22"];

function istNow() {
  const d = new Date(Date.now() + 5.5 * 3600 * 1000);
  return {
    date: d.toISOString().slice(0, 10),
    hour: String(d.getUTCHours()).padStart(2, "0"),
  };
}

async function loadQueue(env, date) {
  const url = `${env.QUEUE_BASE}/queue/${date}.json?t=${Date.now()}`;
  const r = await fetch(url, { cf: { cacheTtl: 0 } });
  if (!r.ok) throw new Error(`Queue file nahi mili: queue/${date}.json (HTTP ${r.status})`);
  return r.json();
}

async function postSlot(env, slot) {
  const { date } = istNow();
  const q = await loadQueue(env, date);
  const p = (q.posts || []).find((x) => x.slot === slot);
  if (!p) return { skipped: `Slot ${slot} ke liye koi post nahi` };

  const imageUrl = p.image.startsWith("http") ? p.image : `${env.QUEUE_BASE}/${p.image}`;
  const body = new URLSearchParams({
    url: imageUrl,
    caption: p.caption,
    access_token: env.FB_PAGE_TOKEN,
  });
  const v = env.GRAPH_VERSION || "v26.0";
  const r = await fetch(`https://graph.facebook.com/${v}/${env.FB_PAGE_ID}/photos`, {
    method: "POST",
    body,
  });
  const j = await r.json();
  if (!r.ok || j.error) throw new Error(`Facebook error: ${JSON.stringify(j.error || j)}`);
  return { posted: slot, date, post_id: j.post_id || j.id };
}

export default {
  // Cron: har slot par apne aap chalta hai
  async scheduled(event, env, ctx) {
    const { hour } = istNow();
    if (!SLOTS.includes(hour)) {
      console.log(`IST hour ${hour} koi slot nahi, skip`);
      return;
    }
    ctx.waitUntil(
      postSlot(env, hour)
        .then((res) => console.log(JSON.stringify(res)))
        .catch((e) => console.error(String(e)))
    );
  },

  // Browser se check / test:
  //   https://<worker>.workers.dev/              → aaj ki queue dekhein (kuch post nahi hota)
  //   https://<worker>.workers.dev/run?slot=07&key=TEST_KEY  → us slot ko abhi post karein
  async fetch(request, env) {
    const u = new URL(request.url);
    const json = (o, s = 200) =>
      new Response(JSON.stringify(o, null, 2), {
        status: s,
        headers: { "content-type": "application/json; charset=utf-8" },
      });

    try {
      if (u.pathname === "/run") {
        if (!env.TEST_KEY || u.searchParams.get("key") !== env.TEST_KEY)
          return json({ error: "Galat key" }, 403);
        const slot = (u.searchParams.get("slot") || "").padStart(2, "0");
        if (!SLOTS.includes(slot)) return json({ error: `slot inme se ho: ${SLOTS.join(", ")}` }, 400);
        return json(await postSlot(env, slot));
      }
      const { date, hour } = istNow();
      const q = await loadQueue(env, date);
      return json({
        ist_date: date,
        ist_hour: hour,
        slots: (q.posts || []).map((p) => ({ slot: p.slot, image: p.image, caption_start: p.caption.slice(0, 60) })),
      });
    } catch (e) {
      return json({ error: String(e.message || e) }, 500);
    }
  },
};
