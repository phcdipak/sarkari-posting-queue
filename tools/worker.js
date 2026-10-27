// ============================================================
//  Sarkari Posting – Facebook Auto Poster (Cloudflare Worker)
//  v2: har ghante (7 AM – 11 PM IST) GitHub queue se us ghante ke
//  saare posts (job + current affairs) Facebook Page par daalta hai.
// ------------------------------------------------------------
//  Variables: QUEUE_BASE, FB_PAGE_ID, FB_PAGE_TOKEN (secret), TEST_KEY (secret)
//  Cron:  30 1-17 * * *   (= 7:00 se 23:00 IST, har ghante)
// ============================================================

const SLOTS = ["07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23"];

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
  if (r.status === 404) return { posts: [] };
  if (!r.ok) throw new Error(`Queue file nahi mili: queue/${date}.json (HTTP ${r.status})`);
  return r.json();
}

async function postOne(env, p) {
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
  return j.post_id || j.id;
}

// Ek slot ke saare posts (job pehle, phir current affairs) ek-ek karke
async function postSlot(env, slot) {
  const { date } = istNow();
  const q = await loadQueue(env, date);
  const items = (q.posts || []).filter((x) => x.slot === slot);
  if (!items.length) return { skipped: `Slot ${slot} ke liye koi post nahi`, date };
  const results = [];
  for (const p of items) {
    try {
      results.push({ image: p.image, post_id: await postOne(env, p) });
    } catch (e) {
      results.push({ image: p.image, error: String(e.message || e) });
    }
  }
  return { slot, date, results };
}

export default {
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

  //   /                          → aaj ki queue dekhein (kuch post nahi hota)
  //   /run?slot=07&key=TEST_KEY  → us slot ke posts abhi daalein
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
        version: 2,
        ist_date: date,
        ist_hour: hour,
        slots: (q.posts || []).map((p) => ({ slot: p.slot, image: p.image, caption_start: p.caption.slice(0, 60) })),
      });
    } catch (e) {
      return json({ error: String(e.message || e) }, 500);
    }
  },
};
