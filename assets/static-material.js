
const params = new URLSearchParams(location.search);
const stimulusId = params.get('stimulus') || params.get('item') || 'S1';
const stimulusIds = (params.get('stimuli') || stimulusId).split(',').map((id) => id.trim()).filter(Boolean);
const conditionRaw = params.get('condition') || params.get('version') || 'original';
const label = params.get('label') || `${stimulusIds.join('-')}_${conditionRaw}`;
const readingStartMs = performance.now();

function normalizeCondition(condition) {
  if (condition === 'helper_2025' || condition === 'dyslexia_helper_2025') return 'helper';
  return condition;
}
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}
function getItem(id) {
  return window.STIMULI.items.find((item) => item.id === id);
}
function highlightDftgenText(value) {
  const englishTagged = String(value ?? '').match(/^(\[[^\]]{1,24}\])\s*(.*)$/);
  if (englishTagged) {
    const tag = escapeHtml(englishTagged[1]);
    const body = englishTagged[2].trim();
    let bodyHtml = escapeHtml(body);
    const keyMatch = body.match(/^(.{2,42}?)(?=\s+(?:was|is|were|are|stood|stands|shows|show|includes|include|contains|dates|date|gave|gives|collected|wears|means|meant|helped|helps|could|has|have|once|comes|came)\b)/i);
    const key = keyMatch ? keyMatch[1].trim() : '';
    if (key && !/^(it|he|she|they|this|these|that|those)$/i.test(key)) {
      const keyHtml = escapeHtml(key);
      bodyHtml = bodyHtml.replace(keyHtml, `<strong class="key-info">${keyHtml}</strong>`);
    }
    return `<mark class="tag">${tag}</mark> ${bodyHtml}`;
  }
  let html = escapeHtml(value);
  html = html.replace(/(^\u3010[^\u3011]{1,10}\u3011)/, '<mark class="tag">$1</mark>');
  html = html.replace(/(<mark class="tag">\u3010(?:器物|主题|内容|价值|用途|看点|寓意|形制|材质|名称|产地|画面|细节)\u3011<\/mark>)([^，。；;]{2,22})/, '$1<strong class="key-info">$2</strong>');
  return html;
}
function visualChunksForDftgen(value) {
  const text = String(value || '').trim();
  const tagMatch = text.match(/^(\u3010[^\u3011]{1,10}\u3011)(.*)$/);
  const tag = tagMatch ? tagMatch[1] : '';
  const body = (tagMatch ? tagMatch[2] : text).trim();
  if (!body) return [text];
  const pieces = body.split(/(?<=[，、；;])/).map((piece) => piece.trim()).filter(Boolean);
  const chunks = [];
  let current = '';
  for (const piece of pieces.length ? pieces : [body]) {
    const prefix = chunks.length === 0 && !current ? tag : '';
    const candidate = current ? `${current}${piece}` : `${prefix}${piece}`;
    if (current && candidate.length > 30) {
      chunks.push(current);
      current = piece;
    } else {
      current = candidate;
    }
  }
  if (current) chunks.push(current);
  return chunks;
}
function dftgenControlsHtml() {
  return `
    <div class="dftgen-controls" aria-label="DFT-GEN reading support settings">
      <button class="dftgen-toggle" type="button" data-dftgen-toggle="space" aria-pressed="false">Spacious spacing</button>
      <button class="dftgen-toggle" type="button" data-dftgen-toggle="mask" aria-pressed="false">Focus mask</button>
    </div>`;
}
function renderOriginalOrHelper(paragraphs, cls) {
  return `<article class="reading-card ${cls}">${paragraphs.map((p) => `<p>${escapeHtml(p)}</p>`).join('')}</article>`;
}
function renderDftgen(paragraphs) {
  return `
    <article class="reading-card reading-card-dftgen">
      <div class="dftgen-toolbar"><span>DFT-GEN Focus</span></div>
      <p class="dftgen-help">You can use spacious spacing or focus mask if it helps you read.</p>
      ${dftgenControlsHtml()}
      <div class="dftgen-blocks">
        ${paragraphs.map((p, index) => {
          const chunks = visualChunksForDftgen(p);
          return `<p class="dftgen-line"><span class="line-no">${index + 1}</span><span>${chunks.map((chunk) => `<span class="dftgen-subline">${highlightDftgenText(chunk)}</span>`).join('')}</span></p>`;
        }).join('')}
      </div>
    </article>`;
}
function renderMaterialBody(paragraphs, condition) {
  if (condition === 'dftgen') return renderDftgen(paragraphs);
  return renderOriginalOrHelper(paragraphs, condition === 'original' ? 'reading-card-original' : 'reading-card-helper');
}
function conditionLabelText(condition, rawCondition) {
  if (rawCondition === 'helper_2025' || condition === 'helper') return 'Dyslexia Helper 2025 ver.';
  if (condition === 'dftgen') return 'DFT-GEN';
  return 'Original';
}
function conditionCode(condition) {
  if (condition === 'helper') return 'H';
  if (condition === 'dftgen') return 'D';
  return 'O';
}
function generateCompletionCode(seconds, condition) {
  const materialKey = stimulusIds.join('').toUpperCase();
  const encodedSeconds = seconds.toString(8).padStart(3, '0');
  return `${conditionCode(condition)}${materialKey}${encodedSeconds}`;
}
function setupDftgenControls() {
  document.querySelectorAll('.reading-card-dftgen').forEach((card) => {
    card.querySelectorAll('[data-dftgen-toggle]').forEach((button) => {
      button.addEventListener('click', () => {
        const mode = button.dataset.dftgenToggle;
        const className = mode === 'space' ? 'dftgen-spacious' : 'dftgen-mask';
        const enabled = !card.classList.contains(className);
        card.classList.toggle(className, enabled);
        button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
        if (mode === 'mask' && enabled && !card.querySelector('.dftgen-line-active')) {
          card.querySelector('.dftgen-line')?.classList.add('dftgen-line-active');
        }
      });
    });
    card.querySelectorAll('.dftgen-line').forEach((line) => {
      line.addEventListener('click', () => {
        if (!card.classList.contains('dftgen-mask')) return;
        card.querySelectorAll('.dftgen-line-active').forEach((active) => active.classList.remove('dftgen-line-active'));
        line.classList.add('dftgen-line-active');
      });
    });
  });
}
function setupFinishReading() {
  const button = document.getElementById('finishReadingButton');
  const result = document.getElementById('readingTimeResult');
  if (!button || !result) return;
  button.addEventListener('click', () => {
    const totalSeconds = Math.max(0, Math.round((performance.now() - readingStartMs) / 1000));
    const completionCode = generateCompletionCode(totalSeconds, normalizeCondition(conditionRaw));
    button.disabled = true;
    button.textContent = 'Completion code generated';
    result.hidden = false;
    result.innerHTML = `
      <strong>Completion code</strong>
      <code class="completion-code">${completionCode}</code>
      <span>Please enter this code in the survey to confirm that you have finished this page.</span>
    `;
    result.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
}
function render() {
  const condition = normalizeCondition(conditionRaw);
  const app = document.getElementById('app');
  const items = stimulusIds.map(getItem);
  const invalidItem = items.find((item) => !item || !item.conditions[condition]);
  if (invalidItem || !items.length) {
    app.innerHTML = `<section class="card"><h1>Invalid material link</h1><p class="error">Please check the stimulus/stimuli and condition parameters.</p></section>`;
    return;
  }
  const conditionLabel = conditionLabelText(condition, conditionRaw);
  app.innerHTML = `
    <section class="card material-shell ${items.length > 1 ? 'material-shell-multiple' : ''}">
      <span class="badge">${escapeHtml(label)}</span>
      <h1>${items.length > 1 ? 'Museum Reading Materials' : escapeHtml(items[0].title)}</h1>
      <p class="muted">Version: ${escapeHtml(conditionLabel)}. Please read the exhibit description carefully. When you finish, return to the survey and continue answering the questions.</p>
      ${items.map((item, index) => `
        <section class="exhibit-block">
          ${items.length > 1 ? `<p class="badge exhibit-order">Exhibit ${index + 1} / ${items.length}</p>` : ''}
          ${items.length > 1 ? `<h2>${escapeHtml(item.title)}</h2>` : ''}
          ${renderMaterialBody(item.conditions[condition] || [], condition)}
        </section>
      `).join('')}
      <section class="finish-panel" aria-label="阅读完成与计时">
        <button class="btn primary finish-reading-button" id="finishReadingButton" type="button">I have finished reading</button>
        <p class="muted small">Click the button only after you have finished reading. Then copy the completion code back to the survey.</p>
        <div class="reading-time-result" id="readingTimeResult" hidden></div>
      </section>
    </section>`;
  setupDftgenControls();
  setupFinishReading();
}
render();
