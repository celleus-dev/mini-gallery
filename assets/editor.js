/* Swatchwork Minis — lasso paint editor (edit.html).
 *
 * Draw around an area to add it to a paint, or switch to Remove to take it away.
 * Nothing is saved to the site from here: "Download edits" saves a small JSON
 * file (the lasso shapes) that's applied with tools/apply_edits.py after review.
 * Work in progress is kept in this browser's storage so a closed tab isn't lost.
 */
(function () {
  "use strict";

  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const v = (url, mini) => (mini && mini.updated ? `${url}?v=${encodeURIComponent(mini.updated)}` : url);
  const hexRgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));

  function store(key, value) {
    try {
      if (value === undefined) return JSON.parse(localStorage.getItem(key) || "null");
      if (value === null) localStorage.removeItem(key);
      else localStorage.setItem(key, JSON.stringify(value));
    } catch (e) { return null; }
  }

  function loadImage(src) {
    return new Promise((res, rej) => {
      const im = new Image();
      im.onload = () => res(im);
      im.onerror = () => rej(new Error("could not load " + src));
      im.src = src;
    });
  }

  async function boot() {
    const main = $("#main");
    let data;
    try {
      data = await (await fetch("data/minis.json", { cache: "no-cache" })).json();
    } catch (e) {
      main.innerHTML = `<div class="empty"><strong>Couldn't load the minis</strong>Try reloading.</div>`;
      return;
    }
    const id = new URLSearchParams(location.search).get("id");
    const mini = (data.minis || []).find((m) => m.id === id);
    if (!mini) return pickList(main, data.minis || []);
    document.title = `Edit ${mini.name} · Swatchwork Minis`;
    editor(main, mini);
  }

  function pickList(main, minis) {
    main.innerHTML = `
      <div class="page-head"><h1>Paint editor</h1>
        <p class="lede">Choose a mini to fine-tune where its paints are.</p></div>
      <div class="grid">${minis.map((m) => `
        <a class="card" href="edit.html?id=${encodeURIComponent(m.id)}">
          <div class="card-img"><img src="${esc(v(m.photo, m))}" alt="" loading="lazy"></div>
          <div class="card-body"><div class="card-title">${esc(m.name)}</div>
          <div class="card-meta">${esc(m.game || "")}</div></div>
        </a>`).join("")}</div>`;
  }

  async function editor(main, mini) {
    const paints = mini.paints || [];
    const draftKey = `swatchwork-edits:${mini.id}:${mini.updated || ""}`;

    main.innerHTML = `
      <div class="page-head">
        <p class="eyebrow"><a href="edit.html">All minis</a> · <a href="mini.html?id=${encodeURIComponent(mini.id)}">View page</a></p>
        <h1>${esc(mini.name)}</h1>
        <p class="lede">Pick a paint, then draw around an area on the photo. Lift your finger or mouse to finish the shape.</p>
      </div>
      <div class="ed-layout">
        <div>
          <div class="ed-tools" role="toolbar" aria-label="Editor tools">
            <label class="ed-group ed-pick"><span class="swatch" id="pick-swatch"></span>
              <span class="visually-hidden">Paint</span>
              <select id="pick">${paints.map((p, i) => `<option value="${i}">${esc(p.name)}</option>`).join("")}</select>
            </label>
            <div class="ed-group" role="group" aria-label="Tool">
              <button class="btn" data-mode="add" aria-pressed="true">+ Add</button>
              <button class="btn" data-mode="remove" aria-pressed="false">− Remove</button>
              <button class="btn" data-mode="pan" aria-pressed="false">Move</button>
            </div>
            <div class="ed-group" role="group" aria-label="Zoom">
              <button class="btn" id="zoom-out" aria-label="Zoom out">−</button>
              <span class="ed-zoom" id="zoom-label">100%</span>
              <button class="btn" id="zoom-in" aria-label="Zoom in">+</button>
            </div>
            <div class="ed-group" role="group" aria-label="Show">
              <button class="btn" data-show="one" aria-pressed="true">This paint</button>
              <button class="btn" data-show="all" aria-pressed="false">All</button>
              <button class="btn" data-show="none" aria-pressed="false">Photo</button>
            </div>
            <div class="ed-group">
              <button class="btn" id="undo" disabled>Undo</button>
              <button class="btn" id="redo" disabled>Redo</button>
            </div>
          </div>
          <div class="viewer ed-scroll" id="scroll">
            <div class="ed-stage" id="stage">
              <img class="ed-photo" id="photo" alt="${esc(mini.name)}">
              <canvas id="overlay"></canvas>
              <canvas id="lasso"></canvas>
            </div>
          </div>
          <p class="hint" id="status">Loading…</p>
        </div>
        <aside>
          <p class="panel-title">Paint</p>
          <ul class="paints" id="paint-list">${paints.map((p, i) => `
            <li><button class="paint" type="button" data-i="${i}" aria-pressed="${i === 0}">
              <span class="swatch" style="background:${esc(p.hex)}"></span>
              <span><span class="paint-name">${esc(p.name)}</span><br>
              <span class="paint-sub">${esc([p.brand, p.role].filter(Boolean).join(" · "))}</span></span>
            </button></li>`).join("")}</ul>
          <p class="panel-title">Your edits</p>
          <p class="lede ed-count" id="count">No edits yet.</p>
          <div class="ed-actions">
            <button class="btn btn-primary" id="download" disabled>Download edits</button>
            <button class="btn" id="discard" disabled>Discard all</button>
          </div>
          <p class="hint">Edits don't change the site by themselves. Send the downloaded file in your chat with Claude; you'll see a review before anything is published.</p>
        </aside>
      </div>`;

    // ---------- load photo and masks ----------
    const photo = await loadImage(v(mini.photo, mini));
    const W = photo.naturalWidth, H = photo.naturalHeight;
    $("#photo").src = photo.src;
    const overlay = $("#overlay"), lasso = $("#lasso");
    [overlay, lasso].forEach((c) => { c.width = W; c.height = H; });
    const octx = overlay.getContext("2d"), lctx = lasso.getContext("2d");

    const scratch = document.createElement("canvas");
    scratch.width = W; scratch.height = H;
    const sctx = scratch.getContext("2d", { willReadFrequently: true });

    const base = new Int16Array(W * H).fill(-1); // which paint each pixel is (-1 = none)
    for (let i = 0; i < paints.length; i++) {
      if (!paints[i].mask) continue;
      try {
        const im = await loadImage(v(paints[i].mask, mini));
        sctx.clearRect(0, 0, W, H);
        sctx.drawImage(im, 0, 0, W, H);
        const a = sctx.getImageData(0, 0, W, H).data;
        for (let p = 0; p < W * H; p++) if (a[p * 4 + 3] > 127 && base[p] === -1) base[p] = i;
      } catch (e) { /* missing mask: paint starts empty */ }
    }
    let owner = base.slice();

    // ---------- state ----------
    let sel = 0, mode = "add", show = "one", zoom = 1;
    let ops = [], redo = [];
    let saved = true;
    const draft = store(draftKey);
    if (draft && Array.isArray(draft.ops) && draft.ops.length) {
      ops = draft.ops.filter((o) => paints.some((p) => p.name === o.paint));
      replay();
      saved = !!draft.saved;
      $("#status").textContent = `Restored ${ops.length} edit${ops.length === 1 ? "" : "s"} from last time` +
        (saved ? " (already downloaded)." : ", not downloaded yet.");
    } else {
      $("#status").textContent = "Ready.";
    }

    // ---------- rasterise one lasso and apply it ----------
    function applyOp(op, target) {
      const idx = paints.findIndex((p) => p.name === op.paint);
      if (idx < 0) return;
      let x0 = W, y0 = H, x1 = 0, y1 = 0;
      op.points.forEach(([x, y]) => { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); });
      x0 = Math.max(0, Math.floor(x0)); y0 = Math.max(0, Math.floor(y0));
      x1 = Math.min(W, Math.ceil(x1) + 1); y1 = Math.min(H, Math.ceil(y1) + 1);
      if (x1 <= x0 || y1 <= y0) return;
      sctx.clearRect(0, 0, W, H);
      sctx.beginPath();
      op.points.forEach(([x, y], k) => (k ? sctx.lineTo(x, y) : sctx.moveTo(x, y)));
      sctx.closePath();
      sctx.fillStyle = "#000";
      sctx.fill();
      const bw = x1 - x0, a = sctx.getImageData(x0, y0, bw, y1 - y0).data;
      for (let yy = y0; yy < y1; yy++) {
        for (let xx = x0; xx < x1; xx++) {
          if (a[((yy - y0) * bw + (xx - x0)) * 4 + 3] <= 127) continue;
          const p = yy * W + xx;
          if (op.op === "add") target[p] = idx;
          else if (target[p] === idx) target[p] = -1;
        }
      }
    }
    function replay() {
      owner = base.slice();
      ops.forEach((o) => applyOp(o, owner));
    }

    // ---------- drawing the overlay ----------
    const rgb = paints.map((p) => hexRgb(p.hex || "#888888"));
    const img = octx.createImageData(W, H);
    function render() {
      const d = img.data;
      for (let p = 0; p < W * H; p++) {
        const o = owner[p], j = p * 4;
        let alpha = 0;
        if (o >= 0 && show !== "none") alpha = o === sel ? 165 : show === "all" ? 120 : 0;
        if (alpha) { const c = rgb[o]; d[j] = c[0]; d[j + 1] = c[1]; d[j + 2] = c[2]; }
        d[j + 3] = alpha;
      }
      octx.putImageData(img, 0, 0);
      const n = ops.length;
      $("#count").textContent = n ? `${n} edit${n === 1 ? "" : "s"}${saved ? " (downloaded)" : " (not downloaded yet)"}` : "No edits yet.";
      $("#undo").disabled = !n;
      $("#redo").disabled = !redo.length;
      $("#download").disabled = !n;
      $("#discard").disabled = !n;
    }
    function changed() {
      saved = false;
      store(draftKey, ops.length ? { ops, saved } : null);
      render();
    }

    // ---------- lasso input ----------
    let pts = null;
    const toImg = (e) => {
      const r = lasso.getBoundingClientRect();
      return [Math.round(((e.clientX - r.left) * W) / r.width * 10) / 10,
              Math.round(((e.clientY - r.top) * H) / r.height * 10) / 10];
    };
    function drawPath() {
      lctx.clearRect(0, 0, W, H);
      if (!pts || pts.length < 2) return;
      const px = W / lasso.getBoundingClientRect().width; // image px per screen px
      lctx.beginPath();
      pts.forEach(([x, y], k) => (k ? lctx.lineTo(x, y) : lctx.moveTo(x, y)));
      lctx.closePath();
      lctx.fillStyle = mode === "add" ? hexA(paints[sel].hex, 0.35) : "rgba(255,255,255,0.25)";
      lctx.fill();
      lctx.lineWidth = 2 * px;
      lctx.setLineDash(mode === "add" ? [] : [6 * px, 4 * px]);
      lctx.strokeStyle = mode === "add" ? "#fff" : "#ff4d6d";
      lctx.stroke();
    }
    function hexA(h, a) { const [r, g, b] = hexRgb(h); return `rgba(${r},${g},${b},${a})`; }

    lasso.addEventListener("pointerdown", (e) => {
      if (mode === "pan" || e.button > 0) return;
      e.preventDefault();
      lasso.setPointerCapture(e.pointerId);
      pts = [toImg(e)];
    });
    lasso.addEventListener("pointermove", (e) => {
      if (!pts) return;
      const p = toImg(e), q = pts[pts.length - 1];
      const minStep = (W / lasso.getBoundingClientRect().width) * 2;
      if (Math.hypot(p[0] - q[0], p[1] - q[1]) >= minStep) { pts.push(p); drawPath(); }
    });
    function finish() {
      if (!pts) return;
      const done = pts; pts = null;
      lctx.clearRect(0, 0, W, H);
      if (done.length < 3) return;
      const op = { paint: paints[sel].name, op: mode, points: done };
      ops.push(op); redo = [];
      applyOp(op, owner);
      changed();
      $("#status").textContent = `${mode === "add" ? "Added to" : "Removed from"} ${paints[sel].name}.`;
    }
    lasso.addEventListener("pointerup", finish);
    lasso.addEventListener("pointercancel", () => { pts = null; lctx.clearRect(0, 0, W, H); });

    // ---------- controls ----------
    function setPressed(selector, el) {
      document.querySelectorAll(selector).forEach((b) => b.setAttribute("aria-pressed", String(b === el)));
    }
    document.querySelectorAll("[data-mode]").forEach((b) => b.addEventListener("click", () => {
      mode = b.dataset.mode; setPressed("[data-mode]", b);
      lasso.classList.toggle("pan", mode === "pan");
    }));
    document.querySelectorAll("[data-show]").forEach((b) => b.addEventListener("click", () => {
      show = b.dataset.show; setPressed("[data-show]", b); render();
    }));
    function selectPaint(i) {
      sel = i;
      setPressed("#paint-list .paint", $(`#paint-list .paint[data-i="${i}"]`));
      $("#pick").value = String(i);
      $("#pick-swatch").style.background = paints[i].hex;
      render();
    }
    document.querySelectorAll("#paint-list .paint").forEach((b) =>
      b.addEventListener("click", () => selectPaint(Number(b.dataset.i))));
    $("#pick").addEventListener("change", (e) => selectPaint(Number(e.target.value)));
    $("#pick-swatch").style.background = paints[0].hex;
    function setZoom(z) {
      const sc = $("#scroll"), cx = (sc.scrollLeft + sc.clientWidth / 2) / sc.scrollWidth,
            cy = (sc.scrollTop + sc.clientHeight / 2) / sc.scrollHeight;
      zoom = Math.min(6, Math.max(1, z));
      $("#stage").style.width = `${zoom * 100}%`;
      $("#zoom-label").textContent = `${Math.round(zoom * 100)}%`;
      sc.scrollLeft = cx * sc.scrollWidth - sc.clientWidth / 2;
      sc.scrollTop = cy * sc.scrollHeight - sc.clientHeight / 2;
    }
    $("#zoom-in").addEventListener("click", () => setZoom(zoom * 1.5));
    $("#zoom-out").addEventListener("click", () => setZoom(zoom / 1.5));
    $("#undo").addEventListener("click", () => { if (ops.length) { redo.push(ops.pop()); replay(); changed(); } });
    $("#redo").addEventListener("click", () => { if (redo.length) { const o = redo.pop(); ops.push(o); applyOp(o, owner); changed(); } });
    $("#discard").addEventListener("click", () => {
      if (!ops.length || !window.confirm("Discard all your edits for this mini?")) return;
      ops = []; redo = []; replay(); changed(); saved = true; render();
    });
    $("#download").addEventListener("click", () => {
      const now = new Date();
      const doc = { mini: mini.id, size: [W, H], photo_updated: mini.updated || null,
                    created: now.toISOString(), edits: ops };
      const stamp = now.toISOString().slice(0, 16).replace(/[-:]/g, "").replace("T", "-");
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([JSON.stringify(doc)], { type: "application/json" }));
      a.download = `${mini.id}-edits-${stamp}.json`;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 2000);
      saved = true; store(draftKey, { ops, saved }); render();
      $("#status").textContent = "Downloaded. Send that file in your chat with Claude.";
    });
    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") { e.preventDefault(); $(e.shiftKey ? "#redo" : "#undo").click(); }
      if (e.key === "Escape" && pts) { pts = null; lctx.clearRect(0, 0, W, H); }
    });
    window.addEventListener("beforeunload", (e) => { if (!saved && ops.length) { e.preventDefault(); e.returnValue = ""; } });

    render();
  }

  boot();
})();
