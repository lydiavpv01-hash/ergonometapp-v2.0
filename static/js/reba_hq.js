(() => {
  const HQ_BASE = 'https://raw.githubusercontent.com/lydiavpv01-hash/ergonometapp-v2.0/main/static/img/reba/';

  function renderGuidesHQ() {
    const list = defs[current] || [];
    const box = document.getElementById('guideGallery');
    const count = document.getElementById('guideCount');
    if (!box || !count) return;

    count.textContent = list.length + ' referencias';
    box.innerHTML = '';

    const a = draft.length === 3
      ? calc(...draft)
      : (active()?.measurements.at(-1)?.angle ?? null);
    const d = dir();

    list.forEach(x => {
      const [img, title, desc, match] = x;
      let hi = false;
      if (a != null && match) {
        try { hi = !!match(a, d); } catch (_) {}
      }

      const e = document.createElement('article');
      e.className = 'guide-item' + (hi ? ' highlight' : '');

      const imageUrl = `${HQ_BASE}${img}.png?v=hq1`;
      e.innerHTML = `
        <div class="guide-img guide-img-hq">
          <img src="${imageUrl}" alt="${title} · ${desc}" loading="lazy" decoding="async">
        </div>
        <div class="guide-meta">
          <b>${title}</b>
          <span>${desc}</span>
        </div>`;
      box.appendChild(e);
    });

    if (!list.length) {
      box.innerHTML = '<div style="grid-column:1/-1;padding:25px;text-align:center;color:#7d857f;font-size:11px;border:1px dashed #d7ddd3;border-radius:10px">Este paso no requiere una galería angular.</div>';
    }
  }

  const style = document.createElement('style');
  style.textContent = `
    .guide-img-hq{height:220px!important;display:flex;align-items:center;justify-content:center;background:#fff;padding:8px;overflow:hidden}
    .guide-img-hq img{width:100%;height:100%;object-fit:contain;display:block;image-rendering:auto}
    @media(max-width:650px){.guide-img-hq{height:190px!important}}
  `;
  document.head.appendChild(style);

  window.renderGuides = renderGuidesHQ;
  renderGuidesHQ();
})();
