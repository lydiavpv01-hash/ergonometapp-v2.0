/* ErgonometApp: paginación física de la sección de fundamento.
   Sólo reorganiza el DOM imprimible; no altera ni guarda datos de evaluaciones. */
(function(){
  function makeJustificationPage(source, rows){
    const page = document.createElement('div');
    page.className = 'paper break justification-paper generated-justification-page';

    const content = document.createElement('div');
    content.className = 'paper-content';

    const sourceHeader = source.querySelector('.repeat-doc-header');
    if(sourceHeader) content.appendChild(sourceHeader.cloneNode(true));

    const body = document.createElement('div');
    body.className = 'justify-body';
    const table = source.querySelector('table.justify').cloneNode(false);
    const thead = source.querySelector('table.justify thead');
    if(thead) table.appendChild(thead.cloneNode(true));
    const tbody = document.createElement('tbody');
    rows.forEach(r => tbody.appendChild(r.cloneNode(true)));
    table.appendChild(tbody);
    body.appendChild(table);
    content.appendChild(body);
    page.appendChild(content);

    const footer = document.createElement('div');
    footer.className = 'page-footer';
    footer.innerHTML = '<span>Documento original</span><span class="physical-page-number"></span>';
    page.appendChild(footer);
    return page;
  }

  function availableHeightPx(page){
    const cssHeightIn = 10.70;
    const pxPerIn = 96;
    return cssHeightIn * pxPerIn;
  }

  function paginate(){
    if(document.documentElement.dataset.matrixPaginated === '1') return;
    const source = document.querySelector('.paper.justification-paper:not(.generated-justification-page)');
    if(!source) { renumber(); return; }
    const tbody = source.querySelector('table.justify tbody');
    if(!tbody) { renumber(); return; }
    const rows = Array.from(tbody.children);
    if(!rows.length) { renumber(); return; }

    const anchor = source;
    const pages = [];
    let currentRows = [];

    function testRows(candidateRows){
      const test = makeJustificationPage(source, candidateRows);
      test.style.position = 'absolute';
      test.style.visibility = 'hidden';
      test.style.left = '-20000px';
      test.style.top = '0';
      test.style.height = '10.70in';
      test.style.minHeight = '10.70in';
      test.style.maxHeight = '10.70in';
      test.style.overflow = 'hidden';
      document.body.appendChild(test);
      const content = test.querySelector('.paper-content');
      const footer = test.querySelector('.page-footer');
      const cs = getComputedStyle(test);
      const padTop = parseFloat(cs.paddingTop)||0, padBottom = parseFloat(cs.paddingBottom)||0;
      const footerH = footer ? footer.getBoundingClientRect().height : 0;
      const limit = availableHeightPx(test) - padTop - padBottom - footerH - 8;
      const needed = content.scrollHeight;
      test.remove();
      return needed <= limit;
    }

    rows.forEach(row => {
      const candidate = currentRows.concat(row);
      if(currentRows.length && !testRows(candidate)){
        pages.push(currentRows);
        currentRows = [row];
      } else {
        currentRows = candidate;
      }
    });
    if(currentRows.length) pages.push(currentRows);

    pages.forEach(group => anchor.parentNode.insertBefore(makeJustificationPage(source, group), anchor));
    source.remove();
    document.documentElement.dataset.matrixPaginated = '1';
    renumber();
  }

  function renumber(){
    const pages = Array.from(document.querySelectorAll('.paper'));
    const total = pages.length;
    pages.forEach((page, index) => {
      let footer = page.querySelector(':scope > .page-footer');
      if(!footer){
        footer = document.createElement('div');
        footer.className = 'page-footer';
        footer.innerHTML = '<span>Documento original</span><span></span>';
        page.appendChild(footer);
      }
      const spans = footer.querySelectorAll('span');
      if(spans.length > 1) spans[1].textContent = 'Página ' + (index+1) + ' I ' + total;
    });
  }

  function run(){ requestAnimationFrame(() => requestAnimationFrame(paginate)); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
  window.addEventListener('beforeprint', () => { paginate(); renumber(); });
})();
