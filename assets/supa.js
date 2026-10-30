/* Swatchwork Minis — where the data comes from.
 * With Supabase set up in assets/config.js, minis and games come from the
 * database and photos/masks from its "gallery" storage bucket. If Supabase is
 * not set up, or can't be reached (e.g. the free project is paused), the site
 * falls back to data/minis.json and the files in this repo. */

(function () {
  "use strict";

  const cfg = window.SWATCHWORK_CONFIG || {};
  const url = (cfg.supabaseUrl || "").replace(/\/+$/, "");
  const key = cfg.supabaseKey || "";
  const enabled = !!(url && key);
  const storageBase = `${url}/storage/v1/object/public/gallery/`;

  async function getJSON(path, fallback) {
    try {
      const r = await fetch(path, { cache: "no-cache" });
      if (!r.ok) return fallback;
      return await r.json();
    } catch (e) {
      return fallback;
    }
  }

  async function rest(table, query) {
    const r = await fetch(`${url}/rest/v1/${table}?${query}`, {
      headers: { apikey: key, Accept: "application/json" },
      cache: "no-cache",
    });
    if (!r.ok) throw new Error(`${table}: ${r.status}`);
    return r.json();
  }

  // Paths in the data are relative ("minis/<id>/photo.jpg"); point them at storage.
  function fromStorage(mini) {
    const m = JSON.parse(JSON.stringify(mini));
    if (m.photo) m.photo = storageBase + m.photo;
    (m.paints || []).forEach((p) => { if (p.mask) p.mask = storageBase + p.mask; });
    m.source = "supabase";
    return m;
  }

  async function loadData() {
    if (enabled) {
      try {
        const [minis, games] = await Promise.all([
          rest("minis", "select=data"),
          rest("games", "select=data"),
        ]);
        if (minis.length) {
          return {
            minis: minis.map((r) => fromStorage(r.data)),
            games: games.map((r) => r.data),
          };
        }
      } catch (e) {
        console.warn("Supabase unavailable, using the repo copy:", e);
      }
    }
    const [m, g] = await Promise.all([
      getJSON("data/minis.json", { minis: [] }),
      getJSON("data/games.json", { games: [] }),
    ]);
    return { minis: m.minis || [], games: g.games || [] };
  }

  // Login client (supabase-js), loaded only on pages that need it.
  let clientPromise = null;
  function client() {
    if (!enabled) return Promise.resolve(null);
    if (!clientPromise) {
      clientPromise = new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2";
        s.onload = () => resolve(window.supabase.createClient(url, key));
        s.onerror = () => reject(new Error("couldn't load the login library"));
        document.head.appendChild(s);
      });
    }
    return clientPromise;
  }

  // The signed-in user's email and whether they may save edits.
  async function whoAmI() {
    const sb = await client();
    if (!sb) return { sb: null, email: null, admin: false };
    const { data } = await sb.auth.getSession();
    const email = data.session ? data.session.user.email : null;
    let admin = false;
    if (email) {
      const r = await sb.rpc("is_admin");
      admin = r.data === true;
    }
    return { sb, email, admin };
  }

  window.Swatchwork = { enabled, loadData, client, whoAmI };
})();
