// Browser-level invariants for the built page. Local dev tool, not CI.
//
// Why this is not a unit test: every check here measures the *rendered* page in
// a real layout engine. The defects it guards are ones a source read cannot see
// -- a fill that resolves to nothing, a label scaled under the legibility floor,
// a title drawn through a data marker. AGENTS.md: "check the artefact, not just
// the source."
//
// Why CDP and not the IDE tab: the editor's browser reverts to its panel width
// (~1024px) moments after a viewport is set, so a screenshot or a measurement
// taken at 1135px silently reports on 1024px. Headless Chrome over the DevTools
// protocol holds an exact width via Emulation.setDeviceMetricsOverride. Node's
// built-in WebSocket does the rest -- no npm install, matching the stdlib-only
// rule the CI workflow states.
//
// CI stays browser-free on purpose (see .github/workflows/ci.yml): the thing
// that guards the page's accuracy has no supply chain to go stale. This is the
// manual pass, run before a chart or a breakpoint changes.
//
// Usage: node tools/verify.mjs [path/to/index.html]
//   Env CHROME=/path/to/chrome overrides the auto-detected browser.
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";
const ROOT = new URL("..", import.meta.url).pathname;
const CHROME = process.env.CHROME || [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/snap/bin/chromium",
].find(existsSync);
if (!CHROME) { console.error("no Chrome found; set CHROME=/path/to/chrome"); process.exit(2); }
const PAGE_URL = "file://" + (process.argv[2] || join(ROOT, "index.html"));
const WIDTHS = [320, 480, 640, 900, 1100, 1134, 1135, 1280, 1600];
const PORT = 9334;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

class CDP {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    ws.onmessage = (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && this.pending.has(m.id)) {
        const p = this.pending.get(m.id);
        this.pending.delete(m.id);
        m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
      }
    };
  }
  send(method, params = {}, sessionId) {
    const id = ++this.id;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    this.ws.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
}

// Everything measured in the page, in one evaluate, per width.
const PROBE = `(() => {
  const out = { vw: innerWidth, overflowX: document.documentElement.scrollWidth > innerWidth,
                scrollW: document.documentElement.scrollWidth };
  const figs = [...document.querySelectorAll('figure[data-chart]')];
  out.charts = figs.map(fig => {
    const id = fig.dataset.chart;
    const svgs = [...fig.querySelectorAll('svg')];
    const vis = svgs.filter(s => getComputedStyle(s).display !== 'none');
    const hidden = svgs.filter(s => getComputedStyle(s).display === 'none');
    const fr = fig.getBoundingClientRect();
    const res = { id, visibleVariants: vis.length, hiddenVariants: hidden.length,
                  figWidth: Math.round(fr.width) };

    if (vis.length === 1) {
      const svg = vis[0];
      const sr = svg.getBoundingClientRect();
      const vb = svg.viewBox.baseVal;
      const sx = sr.width / vb.width;
      const sy = sr.height / vb.height;

      // Every text label's box, in device px, relative to the SVG.
      const labels = [...svg.querySelectorAll('text')].map(t => {
        const b = t.getBBox();
        return { text: (t.textContent || '').trim().slice(0, 34),
                 x: b.x * sx, y: b.y * sy, w: b.width * sx, h: b.height * sy,
                 fs: parseFloat(getComputedStyle(t).fontSize) ||
                     parseFloat(t.getAttribute('font-size')) || 0 };
      }).filter(l => l.text);
      res.labelCount = labels.length;
      // Smallest rendered font size, and the label carrying it.
      // getComputedStyle gives the SPECIFIED size. The SVG is scaled from its
      // viewBox to the rendered box, so what a reader's eye meets is that size
      // times the scale. Reporting the raw number would claim 16px at 320px,
      // where the label is actually about 10px — the exact defect that raised
      // the breakpoint to 1100px.
      const sized = labels.filter(l => l.fs > 0);
      if (sized.length) {
        const withRendered = sized.map(l => ({ ...l, rendered: l.fs * sy }));
        const min = withRendered.reduce((a, b) => (b.rendered < a.rendered ? b : a));
        res.minFontSizePx = +min.rendered.toFixed(2);
        res.minFontSample = min.text;
        res.scale = +sy.toFixed(3);
      }
      // Off-canvas: box outside the SVG's own painted area.
      res.offCanvas = labels.filter(l =>
        l.x < -0.5 || l.y < -0.5 || l.x + l.w > sr.width + 0.5 ||
        l.y + l.h > sr.height + 0.5
      ).map(l => l.text);
      // Overlaps between label boxes.
      const hits = [];
      for (let i = 0; i < labels.length; i++) {
        for (let j = i + 1; j < labels.length; j++) {
          const a = labels[i], b = labels[j];
          const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
          const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
          if (ox > 1 && oy > 1) hits.push(a.text + ' <> ' + b.text);
        }
      }
      res.overlaps = hits;

      // Bands: every url(#...) reference must resolve inside this SVG.
      const own = new Set([...svg.querySelectorAll('[id]')].map(e => e.id));
      const refs = [...svg.querySelectorAll('[fill],[stroke]')]
        .flatMap(e => [e.getAttribute('fill'), e.getAttribute('stroke')])
        .filter(Boolean)
        .map(v => (v.match(/url\\(#([^)]+)\\)/) || [])[1])
        .filter(Boolean);
      res.danglingRefs = [...new Set(refs.filter(r => !own.has(r)))];
      res.bandCount = svg.querySelectorAll('.band').length;

      // Label vs data-mark clearance. The overlap check above compares text to
      // text only, so it reported overlap=0 on a title whose last glyph sat
      // 0.8px from a result marker (Chart 01, wide, found 2026-10-18). This
      // compares each label to each *mark*. A mark is a short, small shape: a
      // gridline (spans the plot) or a hatched region (large area) is
      // background a label may legitimately sit on, so those are excluded by
      // length and area, the same way the three Chart 02 series labels sitting
      // inside the band are not defects.
      // Closest approach between any label and any data mark, reported but not
      // judged. The text-vs-text overlap check above cannot see a label that
      // touches a marker (Chart 01's panel-2 title met the 2022 result cap by
      // 0.8px and overlap was 0). A gap alone is not a defect -- a series label
      // pointing at its own data point sits at gap 0 by design -- so this is a
      // diagnostic to eyeball, not a gate. MAX_MARK_LEN/AREA exclude
      // gridlines and hatched regions, which are background, not marks.
      const MAX_MARK_LEN = 100, MAX_MARK_AREA = 2000;
      const marks = [];
      for (const e of svg.querySelectorAll('line,rect,polygon,circle')) {
        let b; try { b = e.getBBox(); } catch { continue; }
        if (!isFinite(b.width) || (b.width === 0 && b.height === 0)) continue;
        if (Math.hypot(b.width, b.height) > MAX_MARK_LEN) continue;
        if (b.width * b.height > MAX_MARK_AREA) continue;
        const sw = parseFloat(e.getAttribute('stroke-width')) || 1;
        marks.push({ x: b.x - sw/2, r: b.x + b.width + sw/2,
                     y: b.y - sw/2, b: b.y + b.height + sw/2 });
      }
      let minGap = Infinity, minGapLabel = '';
      for (const l of labels) for (const m of marks) {
        const dx = Math.max(m.x - (l.x + l.w), l.x - m.r, 0);
        const dy = Math.max(m.y - (l.y + l.h), l.y - m.b, 0);
        const gap = Math.hypot(dx, dy);
        if (gap < minGap) { minGap = gap; minGapLabel = l.text; }
      }
      res.minMarkGap = minGap === Infinity ? null : +minGap.toFixed(1);
      res.minMarkGapLabel = minGapLabel;
      // aria-labelledby tokens must resolve, and to this SVG's own ids.
      const lab = (svg.getAttribute('aria-labelledby') || '').split(/\\s+/).filter(Boolean);
      res.ariaUnresolved = lab.filter(t => !document.getElementById(t));
      res.ariaForeign = lab.filter(t => {
        const el = document.getElementById(t);
        return el && el.closest('svg') !== svg;
      });
    }
    return res;
  });

  // Accessibility floor and JS independence.
  const main = document.querySelector('main');
  out.mainOpacity = getComputedStyle(main).opacity;
  out.mainTextLen = main.innerText.replace(/\\s+/g, ' ').trim().length;
  out.h1 = document.querySelectorAll('h1').length;
  out.svgInDom = document.querySelectorAll('svg.chart').length;
  out.svgInA11yTree = [...document.querySelectorAll('svg.chart')].filter(s => {
    const st = getComputedStyle(s);
    return st.display !== 'none' && st.visibility !== 'hidden';
  }).length;
  out.draftBanner = !!document.querySelector('[data-draft]');
  out.noindex = !!document.querySelector('meta[name=robots][content*=noindex]');
  return out;
})()`;

async function main() {
  const profile = mkdtempSync(join(tmpdir(), "moe-verify-"));
  const chrome = spawn(
    CHROME,
    ["--headless=new", `--user-data-dir=${profile}`, `--remote-debugging-port=${PORT}`,
     "--disable-gpu", "--no-first-run", "--no-default-browser-check"],
    { stdio: ["ignore", "ignore", "pipe"] }
  );
  let version = null;
  for (let i = 0; i < 60 && !version; i++) {
    await sleep(250);
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      if (r.ok) version = await r.json();
    } catch {}
  }
  if (!version) { chrome.kill("SIGKILL"); throw new Error("chrome did not start"); }

  const ws = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((r, j) => ((ws.onopen = r), (ws.onerror = j)));
  const browser = new CDP(ws);
  const problems = [];
  const lines = [];

  try {
    // --- responsive checks, one page per width ---
    for (const w of WIDTHS) {
      const { targetId } = await browser.send("Target.createTarget", { url: "about:blank" });
      const { sessionId } = await browser.send("Target.attachToTarget", { targetId, flatten: true });
      const call = (m, p) => browser.send(m, p, sessionId);
      await call("Page.enable");
      await call("Emulation.setDeviceMetricsOverride", { width: w, height: 1400, deviceScaleFactor: 1, mobile: false });
      await call("Page.navigate", { url: PAGE_URL + `?cb=${Date.now()}` });
      for (let i = 0; i < 40; i++) {
        const f = await call("Runtime.evaluate", { expression: "document.fonts.status", returnByValue: true });
        if (f.result?.value === "loaded") break;
        await sleep(100);
      }
      await sleep(200);
      const got = await call("Runtime.evaluate", { expression: "innerWidth", returnByValue: true });
      if (got.result.value !== w) {
        problems.push(`${w}px: viewport reported ${got.result.value}`);
        await browser.send("Target.closeTarget", { targetId });
        continue;
      }
      const r = await call("Runtime.evaluate", { expression: PROBE, returnByValue: true });
      if (r.exceptionDetails) {
        problems.push(`${w}px: probe threw ${JSON.stringify(r.exceptionDetails.exception?.description)}`);
      }
      const d = r.result.value;
      const per = d.charts.map(c =>
        `chart ${c.id}: labels=${c.labelCount} minRenderedFont=${c.minFontSizePx}px bands=${c.bandCount} ` +
        `off=${c.offCanvas.length} overlap=${c.overlaps.length} minMarkGap=${c.minMarkGap}px("${c.minMarkGapLabel}") dangling=${c.danglingRefs.length} ` +
        `ariaUnresolved=${c.ariaUnresolved.length} ariaForeign=${c.ariaForeign.length}`
      ).join(" | ");
      lines.push(`${String(w).padStart(4)}px  main=${d.mainOpacity} text=${d.mainTextLen} h1=${d.h1} svgShown=${d.svgInA11yTree}/dom=${d.svgInDom} overflowX=${d.overflowX} draft=${d.draftBanner} noindex=${d.noindex}\n      ${per}`);

      for (const c of d.charts) {
        if (c.visibleVariants !== 1) problems.push(`${w}px chart ${c.id}: ${c.visibleVariants} visible variants`);
        if (c.hiddenVariants !== 1) problems.push(`${w}px chart ${c.id}: ${c.hiddenVariants} hidden variants`);
        if (c.offCanvas.length) problems.push(`${w}px chart ${c.id}: off-canvas ${JSON.stringify(c.offCanvas)}`);
        if (c.overlaps.length) problems.push(`${w}px chart ${c.id}: overlaps ${JSON.stringify(c.overlaps)}`);
        // minMarkGap is reported above, deliberately not a failure: see the
        // probe comment. A gap under ~1px on a title (not a series label) is
        // the pattern to look for by eye.
        if (c.danglingRefs.length) problems.push(`${w}px chart ${c.id}: dangling ${JSON.stringify(c.danglingRefs)}`);
        if (c.ariaUnresolved.length) problems.push(`${w}px chart ${c.id}: aria unresolved ${JSON.stringify(c.ariaUnresolved)}`);
        if (c.ariaForeign.length) problems.push(`${w}px chart ${c.id}: aria points outside own svg ${JSON.stringify(c.ariaForeign)}`);
        if (c.minFontSizePx < 10) problems.push(`${w}px chart ${c.id}: rendered font ${c.minFontSizePx}px "${c.minFontSample}"`);
        if (w >= 1135 && c.minFontSizePx < 16) problems.push(`${w}px chart ${c.id}: wide variant below the 16px floor at ${c.minFontSizePx}px`);
      }
      if (d.overflowX) problems.push(`${w}px: horizontal overflow (scrollW=${d.scrollW})`);
      if (d.h1 !== 1) problems.push(`${w}px: h1 count ${d.h1}`);
      if (d.mainOpacity !== "1") problems.push(`${w}px: main opacity ${d.mainOpacity} with JS`);
      if (d.draftBanner || d.noindex) problems.push(`${w}px: page is marked draft/noindex`);
      if (d.svgInDom !== 4) problems.push(`${w}px: ${d.svgInDom} chart SVGs in the DOM, expected 4`);
      await browser.send("Target.closeTarget", { targetId });
    }

    // --- no-JS: the page must be complete without scripts ---
    {
      const { targetId } = await browser.send("Target.createTarget", { url: "about:blank" });
      const { sessionId } = await browser.send("Target.attachToTarget", { targetId, flatten: true });
      const call = (m, p) => browser.send(m, p, sessionId);
      await call("Page.enable");
      await call("Emulation.setDeviceMetricsOverride", { width: 1280, height: 1400, deviceScaleFactor: 1, mobile: false });
      await call("Emulation.setScriptExecutionDisabled", { value: true });
      await call("Page.navigate", { url: PAGE_URL + "?cb=nojs" });
      await sleep(800);
      const r = await call("Runtime.evaluate", { expression: PROBE, returnByValue: true });
      const d = r.result.value;
      lines.push(`no-JS   main=${d.mainOpacity} text=${d.mainTextLen} svgShown=${d.svgInA11yTree}/dom=${d.svgInDom}`);
      if (d.mainOpacity !== "1") problems.push(`no-JS: main opacity ${d.mainOpacity} — content hidden without scripts`);
      if (d.svgInA11yTree !== 2) problems.push(`no-JS: ${d.svgInA11yTree} variants laid out, expected one per figure`);
      if (d.svgInDom !== 4) problems.push(`no-JS: ${d.svgInDom} svg variants in the DOM, expected 4`);
      await call("Emulation.setScriptExecutionDisabled", { value: false });
      await browser.send("Target.closeTarget", { targetId });
    }

    // --- reduced motion: nothing animating ---
    {
      const { targetId } = await browser.send("Target.createTarget", { url: "about:blank" });
      const { sessionId } = await browser.send("Target.attachToTarget", { targetId, flatten: true });
      const call = (m, p) => browser.send(m, p, sessionId);
      await call("Page.enable");
      await call("Emulation.setDeviceMetricsOverride", { width: 1280, height: 1400, deviceScaleFactor: 1, mobile: false });
      await call("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
      await call("Page.navigate", { url: PAGE_URL + "?cb=rm" });
      await sleep(900);
      const r = await call("Runtime.evaluate", {
        expression: `(() => {
          const anims = document.getAnimations().filter(a => a.playState === 'running');
          const trans = [...document.querySelectorAll('*')].filter(e => {
            const t = getComputedStyle(e).transitionProperty;
            return t && t !== 'all 0s 0s' && !/0s/.test(getComputedStyle(e).transitionDuration);
          });
          const main = getComputedStyle(document.querySelector('main')).opacity;
          return JSON.stringify({ running: anims.length, transitions: trans.length, main });
        })()`,
        returnByValue: true,
      });
      const d = JSON.parse(r.result.value);
      lines.push(`reduced-motion  runningAnimations=${d.running} transitions=${d.transitions} main=${d.main}`);
      if (d.running) problems.push(`reduced-motion: ${d.running} animations running`);
      if (d.transitions) problems.push(`reduced-motion: ${d.transitions} elements still transition`);
      if (d.main !== "1") problems.push(`reduced-motion: main opacity ${d.main}`);
      await browser.send("Target.closeTarget", { targetId });
    }
  } finally {
    ws.close();
    chrome.kill("SIGKILL");
    rmSync(profile, { recursive: true, force: true });
  }

  console.log(lines.join("\n"));
  if (problems.length) {
    console.log("\nPROBLEMS:\n  - " + problems.join("\n  - "));
    process.exit(1);
  }
  console.log("\nALL CHECKS PASS");
}

main().catch((e) => { console.error("error: " + e.message); process.exit(1); });
