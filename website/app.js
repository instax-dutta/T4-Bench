(function () {
  const D = window.BENCH_DATA;
  const $ = s => document.querySelector(s);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches ||
    new URLSearchParams(location.search).get('reduced') === '1';
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };

  function countUp(node, value, decimals, suffix) {
    if (reduced) { node.textContent = value.toFixed(decimals) + suffix; return; }
    const t0 = performance.now(), dur = 650;
    const step = now => {
      const p = Math.max(0, Math.min(1, (now - t0) / dur));
      const e = 1 - Math.pow(1 - p, 3);
      node.textContent = (value * e).toFixed(decimals) + (p === 1 ? suffix : '');
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  function barRow(name, value, display, max, color) {
    const row = el('div', 'bar-row');
    row.append(el('div', 'bar-name', name));
    const track = el('div', 'bar-track'), fill = el('div', 'bar-fill');
    fill.style.setProperty('--bar-color', color);
    fill.dataset.value = String(Math.min(100, value / max * 100));
    track.append(fill);
    const val = el('div', 'bar-value', reduced ? display : '0');
    const m = display.match(/\.(\d+)/);
    const decimals = m ? m[1].length : 0;
    const suffix = display.replace(/[0-9.]/g, '').trim();
    row.append(track, val);
    row._anim = () => {
      fill.style.width = fill.dataset.value + '%';
      countUp(val, value, decimals, suffix ? ' ' + suffix : '');
    };
    return row;
  }

  function bars(id, items, max, color, display) {
    const c = $(id); if (!c) return;
    c.innerHTML = '';
    items.forEach((it, i) => {
      const row = barRow(it.label, it.value, display ? display(it.value, it) : String(it.value),
                         max, color(it, i));
      c.append(row);
      if (reduced) row._anim(); else setTimeout(row._anim, i * 60);
    });
  }

  function table(id, headers, rows) {
    const t = $(id); if (!t) return;
    t.innerHTML = '';
    const h = el('tr'); headers.forEach(x => h.append(el('th', '', x)));
    t.append(el('thead')); t.querySelector('thead').append(h);
    const body = el('tbody');
    rows.forEach(r => { const tr = el('tr'); r.forEach((v, i) => tr.append(el('td', i ? 'num' : '', v))); body.append(tr); });
    t.append(body);
  }

  function pctScore(s) {
    const str = String(s);
    if (str.includes('/') && str.split('/').length === 2) { const [a, b] = str.split('/').map(Number); return Math.round(a / b * 100); }
    if (str.includes('%')) return Number(str.replace(/[^0-9.]/g, ''));
    return null;
  }

  function render() {
    const hot = 'var(--hot)', cool = 'var(--cool)', green = 'var(--green)', ink = 'var(--ink)';
    $('#answers').innerHTML = '';
    $('#machine').textContent = '2× Tesla T4 15 GB · 31 GB RAM · 4 CPU cores · CUDA 13 · PyTorch 2.11 · sm_75 Turing (no BF16 or FP8 hardware)';

    const answers = [
      { label: 'Fastest chat model', name: 'LFM2.5-8B-A1B', big: '119', unit: 'tokens / second' },
      { label: 'Best small agent', name: 'Spark 4B', big: '3/3', unit: 'agent tasks passed' },
      { label: 'Leanest fine-tune', name: 'Unsloth NF4', big: '7.1', unit: 'GB graphics memory' },
      { label: 'Fastest image model', name: 'FLUX.2 klein 4B', big: '374', unit: 'images / hour' },
      { label: 'Best multimodal chat', name: 'Inkling-2-Mini', big: '26', unit: 'tokens / second' },
    ];
    answers.forEach(a => {
      const d = el('div', 'answer');
      d.append(el('div', 'label', a.label), el('strong', '', a.name),
        el('span', 'big', a.big), el('span', 'unit', ' ' + a.unit));
      $('#answers').append(d);
    });

    // Chat models
    const llm = D.llm.slice().sort((a, b) => b.decodeTokS - a.decodeTokS);
    bars('#llm-bars', llm.map(m => ({ label: m.model, value: m.decodeTokS, m })),
      130, (it, i) => i === 0 ? hot : cool, v => v + ' tok/s');
    table('#llm-table', ['Model', 'Reply speed (tok/s)', 'Prompt speed (tok/s)', 'Graphics memory', 'GPUs'],
      llm.map(m => [m.model, m.decodeTokS, m.prefillTokS === null || m.prefillTokS === undefined ? 'n/a' : m.prefillTokS, m.vramGB + ' GB', m.gpus]));
    $('#llm-verdict').textContent = 'LFM2.5-8B-A1B replies about 9× faster than the largest dense model, while using only one of the two GPUs.';

    bars('#concurrency-bars', D.agentConcurrency.map(x => ({ label: x.agents + ' agent' + (x.agents > 1 ? 's' : ''), value: x.agents === 1 ? 71 : 108, extra: x.aggregate })),
      120, (it, i) => i ? green : cool, (v, it) => it.extra);
    bars('#tooleval-bars', D.toolEval.map(x => ({ label: x.metric, value: pctScore(x.score) || 0, raw: x.score }))
        .filter(x => x.value > 0), 100, (it, i) => i === 3 ? hot : cool,
        (v, it) => it.raw);

    // Agents
    bars('#spark-bars', [
      { label: 'Spark 1.7B', value: 2, hint: 'two tasks passed' },
      { label: 'Spark 4B', value: 3, hint: 'three tasks passed' }
    ], 3, (it, i) => i ? hot : cool, (v, it) => it.hint);
    const tb = D.ternary;
    bars('#ternary-bars', [
      { label: 'Ternary 27B · one T4', value: tb.singleT4[0].tg128, hint: 'one GPU' },
      { label: 'Ternary 27B · two T4s', value: tb.dualT4[0].tg128, hint: 'two GPUs' }
    ], 25, (it, i) => i ? green : cool, v => v + ' tok/s');
    table('#spark-table', ['Agent task', 'Spark 1.7B', 'Spark 4B'], D.spark.tasks.map(t => [t.task, t.small, t.large]));

    // Fine-tuning
    const tune = D.fineTuning.results.map(r => ({
      label: r.arm.replace(/`/g, '').replace('soup ', ''),
      value: Math.round(r.peakMiB / 1024 * 10) / 10, raw: r
    }));
    bars('#tune-bars', tune, 16, (it, i) => i < 2 ? green : hot,
      (v, it) => it.raw.result === 'OOM' ? 'OOM' : v + ' GB');
    table('#tune-table', ['Method', 'Result', 'Graphics memory', 'Training loss'],
      D.fineTuning.results.map(r => [r.arm.replace(/`/g, ''), r.result, Math.round(r.peakMiB/1024*10)/10 + ' GB',
        r.loss === null ? 'n/a' : r.loss]));
    $('#tune-verdict').textContent = 'Unsloth uses 7.1 GB. The stock method needs 14.9 GB and runs out of memory with the import blocked. Quality is the same.';

    // Images
    bars('#image-bars', D.imageModels.map(m => ({ label: m.name, value: m.bestThroughput })),
      400, (it, i) => i === 0 ? hot : cool, v => v + ' img/h');
    table('#image-table', ['Model', 'Seconds per image', 'Images per hour', 'Graphics memory', 'Quality score'],
      D.imageModels.map(m => [m.name, m.coldMedian, m.bestThroughput, Math.round(m.peakVramMiB/1024) + ' GB', m.qualityScore]));

    // Video
    bars('#video-bars', D.videoModels.map(m => ({ label: m.model + ' · ' + m.frames + 'f', value: m.perClip })),
      120, (it, i) => i === 0 ? ink : hot, v => v + ' s');
    table('#video-table', ['Configuration', 'Frames', 'Seconds per clip', 'Total seconds', 'Graphics memory', 'Quality score'],
      D.videoModels.map(m => [m.model, m.frames, m.perClip, m.wall, Math.round(m.peakVramMiB/1024) + ' GB', m.qualityScore]));

    // H3
    bars('#h3-bars', D.h3.weightsGiB.map(w => ({ label: w.name, value: w.gib })),
      140, (it, i) => i === 3 ? hot : [ink, 'var(--amber)', green][i] || cool,
      v => v + ' GB');
    table('#h3-table', ['Model precision', 'Memory needed (GB)', 'Fits one T4'],
      D.h3.weightsGiB.map(w => [w.name, w.gib, w.gib <= 15 ? 'yes' : 'no']));

    // Inkling-2-Mini
    const inkData = D.inkling;
    bars('#inkling-bars', inkData.single.map(m => ({ label: m.name, value: m.tg })),
      30, (it, i) => i === 0 ? hot : cool, v => v + ' tok/s');
    table('#inkling-table',
      ['Quant', 'File size', 'Reply speed (tok/s)', 'Prompt speed (tok/s)', 'Graphics memory'],
      inkData.single.map(m => [m.name, m.sizeGiB + ' GB', m.tg, m.pp,
        Math.round(m.peakVramMiB / 1024) + ' GB']));
    table('#inkling-vision-table', ['Vision configuration', 'Seconds per image chat', 'Graphics memory', 'Result'],
      inkData.vision.map(v => [v.config, v.wallS === '' ? 'n/a' : v.wallS,
        Math.round(v.peakVramMiB / 1024) + ' GB', v.result]));
    $('#inkling-verdict').textContent = inkData.engine + '. One T4 runs every quant up to 12.7 GB at 22-26 tok/s; ' + inkData.hybridNote;

    $('#verdicts').textContent = 'Smaller models often win here. A 6B image model outruns the 33B one, an 8B mixture-of-experts chat model outruns a 27B dense one, a smaller text encoder is what lets the video model run at all, and a looped 26B fits one T4 only below 4-bit.';
    $('#limits').innerHTML = '';
    D.limitations.forEach(t => { const li = el('li', '', t); $('#limits').append(li); });
    $('#sources').innerHTML = 'Source: personal research and benchmarking notes from <a href="https://blog.sdad.pro/" target="_blank" rel="noopener">blog.sdad.pro</a>.';
  }

  function initHints() {
    document.querySelectorAll('.table-wrap').forEach(w => {
      const h = el('p', 'table-hint', 'Swipe sideways for every column →');
      w.after(h);
    });
  }
  class MxClip extends HTMLElement {
    connectedCallback() {
      if (this.dataset.ready) return;
      this.dataset.ready = '1';
      const v = document.createElement('video');
      v.className = 'mx-video';
      v.muted = true; v.playsInline = true; v.preload = 'none';
      v.poster = this.getAttribute('poster');
      v.dataset.src = this.getAttribute('src');
      v.setAttribute('aria-label', this.getAttribute('caption') || 'Benchmark diagram');
      const btn = document.createElement('button');
      btn.className = 'mx-replay'; btn.type = 'button'; btn.textContent = 'Replay';
      const cap = document.createElement('div');
      cap.className = 'mx-cap'; cap.textContent = this.getAttribute('caption') || '';
      this.append(btn, v, cap);
      btn.addEventListener('click', () => {
        if (!v.src) v.src = v.dataset.src;
        v.currentTime = 0;
        if (!reduced) v.play().catch(() => {});
      });
      if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver(es => es.forEach(e => {
          if (e.isIntersecting) {
            if (!v.src) v.src = v.dataset.src;
            if (!reduced) v.play().catch(() => {});
          } else if (!v.paused) v.pause();
        }), { threshold: .35 });
        io.observe(this);
      } else { v.src = v.dataset.src; }
    }
  }
  if (!customElements.get('mx-clip')) customElements.define('mx-clip', MxClip);

  render(); initHints();
})();
