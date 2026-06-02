#!/usr/bin/env node

function decodeCompletionCode(code) {
  const normalized = String(code || '').trim().toUpperCase();
  const match = normalized.match(/^([OHD])(S[0-9])([0-7]{3,})$/);
  if (!match) throw new Error(`Invalid completion code format: ${code}`);

  const [, conditionCode, stimulus, encodedSeconds] = match;
  const condition = { O: 'original', H: 'helper_2025', D: 'dftgen' }[conditionCode] || 'unknown';
  const seconds = parseInt(encodedSeconds, 8);

  return { code: normalized, stimulus, condition, reading_time_seconds: seconds };
}

const codes = process.argv.slice(2);
if (!codes.length) {
  console.error('Usage: node decode_completion_codes.js OS1173 [more codes...]');
  process.exit(1);
}

console.log('code,stimulus,condition,reading_time_seconds');
for (const code of codes) {
  try {
    const decoded = decodeCompletionCode(code);
    console.log(`${decoded.code},${decoded.stimulus},${decoded.condition},${decoded.reading_time_seconds}`);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
