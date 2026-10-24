/* Mini Gallery — shared logic for every page.
 * Data lives in data/minis.json (one entry per miniature) and the optional
 * data/games.json (extra details per board game). All URLs are relative so the
 * site works at https://<user>.github.io/mini-gallery/ and on a custom domain. */

(function () {
  "use strict";

  // ---------- helpers ----------
  const $ = (sel, root = document) => root.querySelector(sel);

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function slug(s) {
    return String(s)
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  // Add the mini's "updated" stamp to its file URLs, so a re-processed mini
  // never shows old cached images.
  function v(url, mini) {
    return mini && mini.updated ? `${url}?v=${encodeURIComponent(mini.updated)}` : url;
  }

  function param(name) {
    return new URLSearchParams(location.search).get(name);
  }

  function fmtDate(iso) {
    if (!iso) return "";
    const d = new Date(iso + "T12:00:00");
    if (isNaN(d)) return iso;
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  async function getJSON(path, fallback) {
    try {
      const r = await fetch(path, { cache: "no-cache" });
      if (!r.ok) return fallback;
      return await r.json();
    } catch (e) {
      return fallback;
    }
  }

  async function loadData() {
    const [m, g] = await Promise.all([
      getJSON("data/minis.json", { minis: [] }),
      getJSON("data/games.json", { games: [] }),
    ]);
    const minis = (m.minis || []).slice().sort((a, b) => (b.date || "").localeCompare(a.date || ""));
    const gameInfo = {};
    (g.games || []).forEach((x) => (gameInfo[slug(x.name)] = x));

    // Group minis by board game, newest first within each game
    const games = {};
    minis.forEach((mini) => {
      const key = slug(mini.game || "Unsorted");
      if (!games[key]) {
        games[key] = { slug: key, name: mini.game || "Unsorted", minis: [], info: gameInfo[key] || {} };
      }
      games[key].minis.push(mini);
    });
    const gameList = Object.values(games).sort((a, b) => a.name.localeCompare(b.name));
    return { minis, games, gameList };
  }

  // ---------- shared pieces ----------
  function header(query) {
    const el = $("#site-header");
    if (!el) return;
    el.className = "site-header";
    el.innerHTML = `
      <div class="wrap">
        <a class="brand" href="./">Mini<span>·</span>Gallery</a>
        <form class="search" action="./" method="get" role="search">
          <label class="visually-hidden" for="q">Search minis, games and paints</label>
          <input id="q" name="q" type="search" autocomplete="off"
                 placeholder="Search minis, games or paints" value="${esc(query || "")}">
        </form>
      </div>`;
  }

  function footer() {
    const el = $("#site-footer");
    if (!el) return;
    el.className = "site-footer";
    el.innerHTML = `<div class="wrap">Painted miniatures, sorted by board game.</div>`;
  }

  function card(mini) {
    const dots = (mini.paints || [])
      .slice(0, 8)
      .map((p) => `<span class="dot" style="background:${esc(p.hex)}" title="${esc(p.name)}"></span>`)
      .join("");
    return `
      <a class="card" href="mini.html?id=${encodeURIComponent(mini.id)}">
        <div class="card-img"><img src="${esc(v(mini.photo, mini))}" alt="${esc(mini.name)}" loading="lazy"></div>
        <div class="card-body">
          <div class="card-title">${esc(mini.name)}</div>
          <div class="card-meta">${esc(mini.game || "")}</div>
          <div class="card-swatches">${dots}</div>
        </div>
      </a>`;
  }

  function emptyState(title, text) {
    return `<div class="empty"><strong>${esc(title)}</strong>${esc(text)}</div>`;
  }

  // ---------- search ----------
  function matches(mini, q) {
    const hay = [
      mini.name,
      mini.game,
      mini.notes,
      ...(mini.paints || []).flatMap((p) => [p.name, p.brand]),
    ]
      .join(" ")
      .toLowerCase();
    return q
      .toLowerCase()
      .split(/\s+/)
      .filter(Boolean)
      .every((word) => hay.includes(word));
  }

  // ---------- pages ----------
  async function pageHome() {
    const q = (param("q") || "").trim();
    header(q);
    footer();
    const { minis, gameList } = await loadData();
    const main = $("#main");

    if (q) {
      const hits = minis.filter((m) => matches(m, q));
      document.title = `“${q}” · Mini Gallery`;
      main.innerHTML = `
        <div class="page-head">
          <p class="eyebrow"><a href="./">All games</a></p>
          <h1>Results for “${esc(q)}”</h1>
          <p class="lede">${hits.length} ${hits.length === 1 ? "mini" : "minis"} found</p>
        </div>
        ${hits.length ? `<div class="grid">${hits.map(card).join("")}</div>`
                      : emptyState("Nothing matched", "Try a board game, a mini's name, or a paint like “Nuln Oil”.")}`;
      return;
    }

    if (!minis.length) {
      main.innerHTML = `
        <div class="page-head">
          <h1>Painted miniatures</h1>
          <p class="lede">Sorted by board game, with the paints used on each one.</p>
        </div>
        ${emptyState("No minis yet", "The first painted miniature will show up here.")}`;
      return;
    }

    const chips = gameList
      .map((g) => `<a class="chip" href="game.html?g=${encodeURIComponent(g.slug)}">${esc(g.name)}<span class="n">${g.minis.length}</span></a>`)
      .join("");

    const shelves = gameList
      .map((g) => `
        <section class="shelf">
          <div class="shelf-head">
            <h2><a href="game.html?g=${encodeURIComponent(g.slug)}">${esc(g.name)}</a></h2>
            <a class="see-all" href="game.html?g=${encodeURIComponent(g.slug)}">${g.minis.length} ${g.minis.length === 1 ? "mini" : "minis"} →</a>
          </div>
          <div class="shelf-row">${g.minis.slice(0, 10).map(card).join("")}</div>
        </section>`)
      .join("");

    main.innerHTML = `
      <div class="page-head">
        <h1>Painted miniatures</h1>
        <p class="lede">${minis.length} ${minis.length === 1 ? "mini" : "minis"} across ${gameList.length} ${gameList.length === 1 ? "board game" : "board games"}.</p>
        <nav class="chips" aria-label="Board games">${chips}</nav>
      </div>
      ${shelves}`;
  }

  async function pageGame() {
    header("");
    footer();
    const key = param("g") || "";
    const { games } = await loadData();
    const main = $("#main");
    const g = games[key];

    if (!g) {
      main.innerHTML = `${emptyState("Board game not found", "It may have been renamed.")}<p><a class="back" href="./">← All games</a></p>`;
      return;
    }
    document.title = `${g.name} · Mini Gallery`;

    // Paints used across the whole game, most-used first
    const tally = {};
    g.minis.forEach((m) =>
      (m.paints || []).forEach((p) => {
        const k = p.name.toLowerCase();
        tally[k] = tally[k] || { name: p.name, hex: p.hex, n: 0 };
        tally[k].n++;
      })
    );
    const paints = Object.values(tally).sort((a, b) => b.n - a.n || a.name.localeCompare(b.name));
    const paintCloud = paints
      .map((p) => `<a class="paint-tag" href="./?q=${encodeURIComponent(p.name)}"><span class="dot" style="background:${esc(p.hex)}"></span>${esc(p.name)}<span class="n">${p.n}</span></a>`)
      .join("");

    main.innerHTML = `
      <div class="page-head">
        <p class="eyebrow"><a href="./">All games</a></p>
        <h1>${esc(g.name)}</h1>
        <p class="lede">${g.info.description ? esc(g.info.description) + " " : ""}${g.minis.length} painted ${g.minis.length === 1 ? "mini" : "minis"}.</p>
      </div>
      <div class="grid">${g.minis.map(card).join("")}</div>
      ${paints.length ? `<section class="shelf"><p class="panel-title">Paints used in ${esc(g.name)}</p><div class="paint-cloud">${paintCloud}</div></section>` : ""}`;
  }

  async function pageMini() {
    header("");
    footer();
    const id = param("id") || "";
    const { minis } = await loadData();
    const main = $("#main");
    const mini = minis.find((m) => m.id === id);

    if (!mini) {
      main.innerHTML = `${emptyState("Mini not found", "It may have been renamed or removed.")}<p><a class="back" href="./">← All games</a></p>`;
      return;
    }
    document.title = `${mini.name} · Mini Gallery`;
    const gameSlug = slug(mini.game || "Unsorted");
    const paints = mini.paints || [];
    const mapped = paints.filter((p) => p.mask);

    const paintRows = paints
      .map((p, i) => {
        const sub = [p.brand, p.role].filter(Boolean).map(esc).join(" · ");
        return `
          <li>
            <button class="paint" type="button" data-i="${i}" aria-pressed="false" ${p.mask ? "" : "disabled"}
                    title="${p.mask ? "Show where this paint was used" : "Not highlighted on the photo"}">
              <span class="swatch" style="background:${esc(p.hex)}"></span>
              <span>
                <span class="paint-name">${esc(p.name)}</span><br>
                <span class="paint-sub">${sub}${sub ? " · " : ""}<a href="./?q=${encodeURIComponent(p.name)}">other minis</a></span>
              </span>
            </button>
          </li>`;
      })
      .join("");

    const facts = [
      ["Board game", `<a href="game.html?g=${encodeURIComponent(gameSlug)}">${esc(mini.game || "Unsorted")}</a>`],
      mini.date ? ["Finished", esc(fmtDate(mini.date))] : null,
    ].filter(Boolean);

    const ratio = mini.width && mini.height ? `aspect-ratio:${mini.width}/${mini.height};` : "";

    main.innerHTML = `
      <div class="page-head">
        <p class="eyebrow"><a href="game.html?g=${encodeURIComponent(gameSlug)}">${esc(mini.game || "Unsorted")}</a></p>
        <h1>${esc(mini.name)}</h1>
      </div>
      <div class="mini-layout">
        <div>
          <div class="viewer">
            <div class="viewer-stage" id="stage" style="${ratio}">
              <img class="base" src="${esc(v(mini.photo, mini))}" alt="${esc(mini.name)}">
            </div>
            ${mapped.length ? `
            <div class="viewer-bar">
              <button class="btn" type="button" id="btn-map" aria-pressed="false">Show all paints</button>
              <button class="btn" type="button" id="btn-clear">Clear</button>
            </div>` : ""}
          </div>
          ${mapped.length ? `<p class="hint">Tap a paint to light up where it was used. Shading, washes and metallics are approximate.</p>` : ""}
        </div>
        <aside>
          <p class="panel-title">Paints</p>
          ${paints.length ? `<ul class="paints">${paintRows}</ul>` : `<p class="lede">No paints listed.</p>`}
          <dl class="facts">${facts.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>
          ${mini.notes ? `<p class="panel-title">Notes</p><p class="notes">${esc(mini.notes)}</p>` : ""}
          <a class="back" href="game.html?g=${encodeURIComponent(gameSlug)}">← More from ${esc(mini.game || "this game")}</a>
        </aside>
      </div>`;

    if (mapped.length) setupViewer(mini);
  }

  // ---------- paint highlight viewer ----------
  function setupViewer(mini) {
    const stage = $("#stage");
    const paints = mini.paints || [];
    const layers = {}; // index -> { spot, tint }

    paints.forEach((p, i) => {
      if (!p.mask) return;
      const maskCss = `url("${v(p.mask, mini)}")`;

      // Spotlight layer: the full-colour photo, visible only inside this paint's region
      // (outer element carries the glow, since a filter on the masked element itself gets masked away)
      const spot = document.createElement("div");
      spot.className = "layer spot";
      spot.style.filter = `drop-shadow(0 0 1.5px ${p.hex}) drop-shadow(0 0 1.5px ${p.hex})`;
      const inner = document.createElement("div");
      inner.className = "spot-inner";
      inner.style.backgroundImage = `url("${v(mini.photo, mini)}")`;
      inner.style.webkitMaskImage = maskCss;
      inner.style.maskImage = maskCss;
      spot.appendChild(inner);

      // Map layer: flat paint colour over the region
      const tint = document.createElement("div");
      tint.className = "layer tint";
      tint.style.backgroundColor = p.hex;
      tint.style.webkitMaskImage = maskCss;
      tint.style.maskImage = maskCss;

      stage.appendChild(tint);
      stage.appendChild(spot);
      layers[i] = { spot, tint };
    });

    const buttons = Array.from(document.querySelectorAll(".paint[data-i]"));
    const btnMap = $("#btn-map");
    const btnClear = $("#btn-clear");
    const selected = new Set();
    let mapMode = false;

    function render() {
      const anySpot = selected.size > 0 && !mapMode;
      stage.classList.toggle("dimmed", anySpot || mapMode);
      Object.entries(layers).forEach(([i, l]) => {
        const on = selected.has(Number(i));
        l.spot.classList.toggle("on", !mapMode && on);
        l.tint.classList.toggle("on", mapMode);
      });
      buttons.forEach((b) => b.setAttribute("aria-pressed", String(!mapMode && selected.has(Number(b.dataset.i)))));
      if (btnMap) btnMap.setAttribute("aria-pressed", String(mapMode));
    }

    buttons.forEach((b) =>
      b.addEventListener("click", () => {
        const i = Number(b.dataset.i);
        if (mapMode) {
          mapMode = false;
          selected.clear();
        }
        selected.has(i) ? selected.delete(i) : selected.add(i);
        render();
      })
    );
    if (btnMap)
      btnMap.addEventListener("click", () => {
        mapMode = !mapMode;
        if (mapMode) selected.clear();
        render();
      });
    if (btnClear)
      btnClear.addEventListener("click", () => {
        mapMode = false;
        selected.clear();
        render();
      });
  }

  // ---------- boot ----------
  const page = document.body.dataset.page;
  if (page === "home") pageHome();
  else if (page === "game") pageGame();
  else if (page === "mini") pageMini();
})();
