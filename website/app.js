(function () {
  const D = window.BENCH_DATA;
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
  const colors = { 'flux2-klein-4b': 'var(--verm)', 'qwen-image-2.1-viggle-4step': 'var(--teal)', 'z-image-turbo': 'var(--green)', 'sdxl': 'var(--ink)' };
  const videoColors = { 'cog_s50_f49': 'var(--ink)', 'ltx2b_s8_f121': 'var(--verm)', 'ltx_multi3': 'var(--teal)', 'ltx_multi3_s4_f49': 'var(--green)' };
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    || new URLSearchParams(location.search).get('reduced') === '1';

  function fillMachine() {
    const facts = [['GPUs', D.server.gpus + '× ' + D.server.gpu], ['Architecture', D.server.arch],
      ['Host RAM', D.server.ramGiB + ' GB'], ['CUDA', D.server.cuda], ['PyTorch', D.server.torch]];
    const dl = $('#machine-facts');
    facts.forEach(([k, v]) => { dl.append(el('dt', '', k), el('dd', '', v)); });
    $('#hero-image-name').textContent = D.winners.image;
    $('#hero-image-number').textContent = D.winners.imageThroughput;
    $('#strip-image').textContent = D.winners.imageThroughput;
    $('#strip-video').textContent = D.winners.steadyClipSeconds;
    const ratio = D.winners.cogSeconds / D.winners.steadyClipSeconds;
    $('#strip-ratio').textContent = Math.round(ratio) + '×';
    $('#strip-ratio-label').textContent = Math.round(ratio) + '× slower CogVideoX for the same 49 frames';
  }

  function barRow(name, value, display, max, color) {
    const row = el('div', 'bar-row');
    row.append(el('div', 'bar-name', name));
    const track = el('div', 'bar-track');
    const fill = el('div', 'bar-fill');
    fill.style.setProperty('--bar-color', color);
    fill.dataset.value = String(Math.min(100, value / max * 100));
    track.append(fill);
    const val = el('div', 'bar-value', reduced ? display : '0');
    val.dataset.num = String(value);
    const m = display.match(/\.(\d+)/);
    val.dataset.decimals = String(m ? m[1].length : 0);
    val.dataset.suffix = display.replace(/[0-9.]/g, '').trim();
    row.append(track, val);
    return row;
  }
  function countTo(node, target, decimals) {
    if (reduced) { node.textContent = target.toFixed(decimals) + (node.dataset.suffix ? ' ' + node.dataset.suffix : ''); return; }
    const start = performance.now(), dur = 720;
    function step(now) {
      const p = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      node.textContent = (target * eased).toFixed(decimals) + (p === 1 && node.dataset.suffix ? ' ' + node.dataset.suffix : '');
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function animateBars(container) {
    $$('.bar-row', container).forEach((row, i) => {
      const fill = $('.bar-fill', row), val = $('.bar-value', row);
      const run = () => {
        fill.style.width = fill.dataset.value + '%';
        countTo(val, Number(val.dataset.num), Number(val.dataset.decimals));
      };
      if (reduced) run(); else setTimeout(run, i * 70);
    });
  }
  function renderImageBars() {
    const c = $('#image-bars'); c.innerHTML = '';
    const metrics = {
      throughput: { get: m => m.bestThroughput, max: 400, fmt: v => v + ' img/h', note: 'Best measured configuration for each model on both GPUs.' },
      clip: { get: m => m.qualityScore, max: 100, fmt: v => v + ' pts', note: 'A simple 0-100 score for how well the picture matches the prompt. Higher is better.' },
      vram: { get: m => Math.round(m.peakVramMiB / 1024), max: 8, fmt: v => v + ' GB', note: 'Graphics memory used on one GPU. Lower leaves more room to work.' }
    };
    const metric = metrics[$('.tabs button[aria-selected=true]').dataset.metric];
    D.imageModels.forEach(m => {
      const v = metric.get(m);
      c.append(barRow(m.name, v, metric.fmt(v), metric.max, colors[m.id] || 'var(--ink)'));
    });
    $('#image-note').textContent = metric.note;
    animateBars(c);
  }
  function renderQualityBars() {
    const c = $('#quality-bars'); c.innerHTML = '';
    D.imageModels.slice().sort((a, b) => b.qualityScore - a.qualityScore).forEach(m => {
      c.append(barRow(m.name, m.qualityScore, m.qualityScore + ' pts', 100,
        colors[m.id] || 'var(--ink)'));
    });
    animateBars(c);
  }
  function renderVideoBars() {
    const c = $('#video-bars'); c.innerHTML = '';
    D.videoModels.forEach(m => {
      const label = m.model + ' · ' + m.frames + 'f' + (m.clips > 1 ? ' · ' + m.clips + ' clips' : '');
      c.append(barRow(label, m.perClip, m.perClip + ' s/clip', 1100,
        videoColors[m.id] || 'var(--ink)'));
    });
    c.append(el('p', 'chart-note', 'Shorter is better. Warm rows show the median per-clip time; the total wall time for the three-clip runs is in the table.'));
    animateBars(c);
  }
  function renderH3Bars() {
    const c = $('#h3-bars'); c.innerHTML = '';
    const items = [['BF16', 126.0, 'var(--ink)'], ['FP8', 64.1, 'var(--amber)'],
      ['4-bit', 33.1, 'var(--green)'], ['One T4', 15, 'var(--verm)']];
    items.forEach(([n, v, col]) => c.append(barRow(n, v, v + ' GB', 140, col)));
    animateBars(c);
  }
  function table(id, headers, rows) {
    const t = $(id); t.innerHTML = '';
    const thead = el('thead'), tr = el('tr');
    headers.forEach((h, i) => { const th = el('th', i ? 'num' : '', h); tr.append(th); });
    thead.append(tr); t.append(thead);
    const tb = el('tbody');
    rows.forEach(r => { const row = el('tr'); r.forEach((v, i) => row.append(el('td', i ? 'num' : '', String(v)))); tb.append(row); });
    t.append(tb);
  }
  function renderTables() {
    table('#image-table', ['Model', 'Steps', 'Seconds per image', 'Images per hour', 'Graphics memory', 'Quality score'],
      D.imageModels.map(m => [m.name, m.steps, m.coldMedian, m.bestThroughput, Math.round(m.peakVramMiB/1024) + ' GB', m.qualityScore]));
    table('#video-table', ['Configuration', 'Frames', 'Clips', 'Seconds per clip', 'Total seconds', 'Graphics memory', 'Quality score'],
      D.videoModels.map(m => [m.model, m.frames, m.clips, m.perClip, m.wall, Math.round(m.peakVramMiB/1024) + ' GB', m.qualityScore]));
    table('#h3-table', ['Model precision', 'Memory needed (GB)', 'Fits on one T4'],
      D.h3.weightsGiB.map(w => [w.name, w.gib, w.gib <= 15 ? 'yes' : 'no']));
  }
  function renderNotes() {
    $('#verdicts').textContent = 'Image: ' + D.winners.image + ' is both fastest (' + D.winners.imageThroughput +
      ' images/hour) and best at following the prompt (' + Math.round(D.winners.imageClip * 100) + '/100). Video: the small LTX 2B model is the practical winner at ' +
      D.winners.steadyClipSeconds + ' seconds per short clip. CogVideoX follows the prompt slightly better but takes about 38 times longer.';
    const ul = $('#limits'); D.limitations.forEach(t => ul.append(el('li', '', t)));
    $('#sources').textContent = 'Authoritative tables: benchmarks/image-models/benchmark, benchmarks/video-generation/benchmark, benchmarks/minimax-h3-image/benchmark.';
  }
  function moveIndicator() {
    const tabs = $('.tabs'), active = $('.tabs button[aria-selected=true]'), ind = $('.tab-indicator');
    if (!active) return;
    ind.style.width = active.offsetWidth + 'px';
    ind.style.transform = 'translateX(' + active.offsetLeft + 'px)';
  }
  function initTabs() {
    const params = new URLSearchParams(location.search);
    const requested = params.get('metric') || (['throughput', 'clip', 'vram'].includes(params.get('state')) ? params.get('state') : null);
    if (requested) {
      const match = $$('.tabs button').find(b => b.dataset.metric === requested);
      if (match) {
        $$('.tabs button').forEach(x => x.setAttribute('aria-selected', 'false'));
        match.setAttribute('aria-selected', 'true');
      }
    }
    $$('.tabs button').forEach(b => b.addEventListener('click', () => {
      $$('.tabs button').forEach(x => x.setAttribute('aria-selected', 'false'));
      b.setAttribute('aria-selected', 'true');
      moveIndicator(); renderImageBars();
    }));
    window.addEventListener('resize', moveIndicator);
    moveIndicator();
  }
  function initTableHints() {
    $$('.table-wrap').forEach(w => {
      const h = el('p', 'table-hint', 'Swipe table sideways for all columns →');
      w.after(h);
    });
  }
  function initReplay() {
    $$('.replay').forEach(b => b.addEventListener('click', () => {
      const name = b.dataset.replay;
      const v = $$('.lazy-video').find(x => (x.dataset.src || '').indexOf(name) >= 0);
      if (v) { v.currentTime = 0; if (!reduced) v.play().catch(() => {}); }
    }));
  }
  function initClips() {
    const vids = $$('.lazy-video');
    if (!('IntersectionObserver' in window)) {
      vids.forEach(v => { v.src = v.dataset.src; if (!reduced) v.play().catch(() => {}); });
      return;
    }
    const io = new IntersectionObserver(entries => entries.forEach(e => {
      const v = e.target;
      if (e.isIntersecting) {
        if (!v.src) v.src = v.dataset.src;
        if (!reduced) v.play().catch(() => {});
      } else if (!v.paused) v.pause();
    }), { threshold: 0.35 });
    vids.forEach(v => io.observe(v));
  }
  fillMachine(); initTabs(); renderImageBars(); renderVideoBars(); renderH3Bars(); renderTables(); renderQualityBars(); renderNotes(); initTableHints(); initReplay(); initClips();
})();
