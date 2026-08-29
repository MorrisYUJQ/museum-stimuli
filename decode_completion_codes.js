#!/usr/bin/env node

function decodeCompletionCode(code) {
  const normalized = String(code || '').trim().toUpperCase();
  const match = normalized.match(/^([OHD])(S[0-9])([0-7]{3,})(?:-F(\d+)L(\d{3})A(\d{3})W(\d{3})X(\d)(\d)(\d)(\d)E([01])M(\d+)C(\d+)R(\d+))?$/);
  if (!match) throw new Error(`Invalid completion code format: ${code}`);

  const [, conditionCode, stimulus, encodedSeconds, fontSize, lineSpacing, letterSpacing, wordSpacing,
    fontChanges, lineChanges, letterChanges, wordChanges, maskEnabled, maskToggles, focusMoves, resets] = match;
  const condition = { O: 'original', H: 'helper_2025', D: 'dftgen' }[conditionCode] || 'unknown';
  const seconds = parseInt(encodedSeconds, 8);

  return {
    code: normalized,
    stimulus,
    condition,
    reading_time_seconds: seconds,
    final_font_px: fontSize || '',
    final_line_spacing: lineSpacing ? Number(lineSpacing) / 100 : '',
    final_letter_spacing_em: letterSpacing ? Number(letterSpacing) / 1000 : '',
    final_word_spacing_em: wordSpacing ? Number(wordSpacing) / 1000 : '',
    font_adjustments: fontChanges || '',
    line_adjustments: lineChanges || '',
    letter_adjustments: letterChanges || '',
    word_adjustments: wordChanges || '',
    final_focus_mask_enabled: maskEnabled || '',
    focus_mask_toggles: maskToggles || '',
    focus_line_moves: focusMoves || '',
    resets: resets || ''
  };
}

const codes = process.argv.slice(2);
if (!codes.length) {
  console.error('Usage: node decode_completion_codes.js OS1173 [more codes...]');
  process.exit(1);
}

const columns = [
  'code', 'stimulus', 'condition', 'reading_time_seconds', 'final_font_px',
  'final_line_spacing', 'final_letter_spacing_em', 'final_word_spacing_em',
  'font_adjustments', 'line_adjustments', 'letter_adjustments', 'word_adjustments',
  'final_focus_mask_enabled', 'focus_mask_toggles', 'focus_line_moves', 'resets'
];
console.log(columns.join(','));
for (const code of codes) {
  try {
    const decoded = decodeCompletionCode(code);
    console.log(columns.map((column) => decoded[column]).join(','));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
