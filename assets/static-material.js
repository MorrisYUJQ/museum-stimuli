
const params = new URLSearchParams(location.search);
const stimulusId = params.get('stimulus') || params.get('item') || 'S1';
const stimulusIds = (params.get('stimuli') || stimulusId).split(',').map((id) => id.trim()).filter(Boolean);
const conditionRaw = params.get('condition') || params.get('version') || 'original';
const label = params.get('label') || `${stimulusIds.join('-')}_${conditionRaw}`;
const readingStartMs = performance.now();
const defaultReadingSettings = {
  fontSize: 20,
  lineSpacing: 2.4,
  letterSpacing: 0.02,
  wordSpacing: 0
};
const interactionState = {
  settings: { ...defaultReadingSettings },
  changes: { fontSize: 0, lineSpacing: 0, letterSpacing: 0, wordSpacing: 0 },
  maskEnabled: false,
  maskToggles: 0,
  focusMoves: 0,
  resets: 0
};

function normalizeCondition(condition) {
  if (condition === 'helper_2025' || condition === 'dyslexia_helper_2025') return 'helper';
  return condition;
}
function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
}
function escapeRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
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
    const answerTerms = [
      'X-ray fluorescence',
      'Panathenaic festival',
      'religious procession',
      'power and wealth',
      'Late Period',
      'Bubastis',
      '432 BC',
      'Athena',
      'Bastet',
      'rebirth',
      'Scientists'
    ];
    let answerHighlighted = false;
    for (const term of answerTerms) {
      const escapedTerm = escapeHtml(term);
      const pattern = new RegExp(`\\b${escapeRegex(escapedTerm)}\\b`, 'i');
      bodyHtml = bodyHtml.replace(pattern, (match) => {
        answerHighlighted = true;
        return `<strong class="key-info">${match}</strong>`;
      });
    }
    if (answerHighlighted) return `<mark class="tag">${tag}</mark> ${bodyHtml}`;

    const keyMatch = body.match(/^(.{2,58}?)(?=\s+(?:was|is|were|are|stood|stands|show|shows|showed|display|displays|exhibit|exhibits|feature|features|illustrate|illustrates|represent|represents|explain|explains|include|includes|contain|contains|date|dates|gave|gives|donated|collected|wears|symbolise|symbolises|invoke|invoked|investigate|investigated|mean|means|meant|hoped|helped|helps|could|has|have|come|comes|came)\b)/i);
    let key = keyMatch ? keyMatch[1].trim() : '';
    key = key.replace(/^(the|a|an|its|her|his|their|this|these)\s+/i, '');
    const words = key.split(/\s+/).filter(Boolean);
    if (words.length > 5) key = '';
    if (key && !/^(it|he|she|they|this|these|that|those|inside)$/i.test(key)) {
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
    <div class="reading-settings" aria-label="DFT-GEN reading display settings">
      <div class="reading-setting">
        <label for="fontSize">Font size <output id="fontSizeValue">20px</output></label>
        <input id="fontSize" data-reading-setting="fontSize" type="range" min="16" max="32" step="1" value="20">
      </div>
      <div class="reading-setting">
        <label for="lineSpacing">Line spacing <output id="lineSpacingValue">2.40</output></label>
        <input id="lineSpacing" data-reading-setting="lineSpacing" type="range" min="1.4" max="3" step="0.1" value="2.4">
      </div>
      <div class="reading-setting">
        <label for="letterSpacing">Letter spacing <output id="letterSpacingValue">0.02em</output></label>
        <input id="letterSpacing" data-reading-setting="letterSpacing" type="range" min="0" max="0.12" step="0.01" value="0.02">
      </div>
      <div class="reading-setting">
        <label for="wordSpacing">Word spacing <output id="wordSpacingValue">0.00em</output></label>
        <input id="wordSpacing" data-reading-setting="wordSpacing" type="range" min="0" max="0.24" step="0.02" value="0">
      </div>
    </div>
    <div class="dftgen-controls">
      <button class="dftgen-toggle" type="button" data-dftgen-toggle="mask" aria-pressed="false">Focus mask</button>
      <button class="dftgen-toggle dftgen-reset" type="button" data-reading-reset>Reset settings</button>
    </div>`;
}
function renderOriginalOrHelper(paragraphs, cls) {
  return `<article class="reading-card ${cls}">${paragraphs.map((p) => `<p>${escapeHtml(p)}</p>`).join('')}</article>`;
}
function renderDftgen(paragraphs) {
  return `
    <article class="reading-card reading-card-dftgen">
      <div class="dftgen-toolbar"><span>DFT-GEN Focus</span></div>
      <p class="dftgen-help">Adjust the display if it helps you read. These settings do not change the text.</p>
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
function telemetrySuffix() {
  const settings = interactionState.settings;
  const changes = interactionState.changes;
  return [
    `F${Math.round(settings.fontSize)}`,
    `L${String(Math.round(settings.lineSpacing * 100)).padStart(3, '0')}`,
    `A${String(Math.round(settings.letterSpacing * 1000)).padStart(3, '0')}`,
    `W${String(Math.round(settings.wordSpacing * 1000)).padStart(3, '0')}`,
    `X${Math.min(changes.fontSize, 9)}${Math.min(changes.lineSpacing, 9)}${Math.min(changes.letterSpacing, 9)}${Math.min(changes.wordSpacing, 9)}`,
    `E${interactionState.maskEnabled ? 1 : 0}`,
    `M${interactionState.maskToggles}`,
    `C${interactionState.focusMoves}`,
    `R${interactionState.resets}`
  ].join('');
}
function updateReadingSetting(card, key, value) {
  const numericValue = Number(value);
  interactionState.settings[key] = numericValue;
  const cssVariables = {
    fontSize: ['--reading-font-size', `${numericValue}px`],
    lineSpacing: ['--reading-line-spacing', numericValue],
    letterSpacing: ['--reading-letter-spacing', `${numericValue}em`],
    wordSpacing: ['--reading-word-spacing', `${numericValue}em`]
  };
  const [property, cssValue] = cssVariables[key];
  card.style.setProperty(property, cssValue);
  const output = card.querySelector(`#${key}Value`);
  if (output) {
    output.textContent = key === 'fontSize'
      ? `${Math.round(numericValue)}px`
      : key === 'lineSpacing'
        ? numericValue.toFixed(2)
        : `${numericValue.toFixed(2)}em`;
  }
}
function setupDftgenControls() {
  document.querySelectorAll('.reading-card-dftgen').forEach((card) => {
    card.querySelectorAll('[data-reading-setting]').forEach((control) => {
      const key = control.dataset.readingSetting;
      control.addEventListener('input', () => updateReadingSetting(card, key, control.value));
      control.addEventListener('change', () => {
        interactionState.changes[key] += 1;
      });
      updateReadingSetting(card, key, control.value);
    });
    card.querySelectorAll('[data-dftgen-toggle]').forEach((button) => {
      button.addEventListener('click', () => {
        const mode = button.dataset.dftgenToggle;
        const className = 'dftgen-mask';
        const enabled = !card.classList.contains(className);
        card.classList.toggle(className, enabled);
        button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
        interactionState.maskEnabled = enabled;
        interactionState.maskToggles += 1;
        if (mode === 'mask' && enabled && !card.querySelector('.dftgen-line-active')) {
          card.querySelector('.dftgen-line')?.classList.add('dftgen-line-active');
        }
      });
    });
    card.querySelector('[data-reading-reset]')?.addEventListener('click', () => {
      Object.entries(defaultReadingSettings).forEach(([key, value]) => {
        const control = card.querySelector(`[data-reading-setting="${key}"]`);
        if (control) control.value = value;
        updateReadingSetting(card, key, value);
      });
      card.classList.remove('dftgen-mask');
      card.querySelector('[data-dftgen-toggle="mask"]')?.setAttribute('aria-pressed', 'false');
      interactionState.maskEnabled = false;
      interactionState.resets += 1;
    });
    card.querySelectorAll('.dftgen-line').forEach((line) => {
      line.addEventListener('click', () => {
        if (!card.classList.contains('dftgen-mask')) return;
        if (line.classList.contains('dftgen-line-active')) return;
        card.querySelectorAll('.dftgen-line-active').forEach((active) => active.classList.remove('dftgen-line-active'));
        line.classList.add('dftgen-line-active');
        interactionState.focusMoves += 1;
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
    const condition = normalizeCondition(conditionRaw);
    const baseCode = generateCompletionCode(totalSeconds, condition);
    const completionCode = condition === 'dftgen' ? `${baseCode}-${telemetrySuffix()}` : baseCode;
    button.disabled = true;
    button.textContent = 'Completion code generated';
    result.hidden = false;
    result.innerHTML = `
      <strong>Completion code</strong>
      <code class="completion-code">${completionCode}</code>
      <span>Please enter this code in the survey to confirm that you have finished this page.</span>
      <span class="return-survey-hint"><strong>After copying the code, close this reading-material tab immediately and return to the survey. Please do not reopen the material while answering the questions.</strong></span>
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
