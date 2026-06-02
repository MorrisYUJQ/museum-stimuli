#!/usr/bin/env node

function codeSalt(key) {
  return Array.from(key).reduce((sum, char) => sum + char.charCodeAt(0), 73);
}

function checksum(value) {
  const sum = Array.from(value).reduce((acc, char, index) => acc + char.charCodeAt(0) * (index + 3), 0);
  return (sum % 1296).toString(36).toUpperCase().padStart(2, '0');
}

function decodeCompletionCode(code) {
  const normalized = String(code || '').trim().toUpperCase();
  const match = normalized.match(/^M-([A-Z0-9]+)-([A-Z0-9]+)-([A-Z0-9]{2})$/);
  if (!match) throw new Error(`Invalid completion code format: ${code}`);

  const [, materialKey, encodedSeconds, check] = match;
  const expectedCheck = checksum(`${materialKey}:${encodedSeconds}`);
  if (check !== expectedCheck) throw new Error(`Checksum mismatch: ${code}`);

  const encodedValue = parseInt(encodedSeconds, 36);
  const seconds = (encodedValue - codeSalt(materialKey)) / 17;
  if (!Number.isInteger(seconds) || seconds < 0) throw new Error(`Invalid encoded seconds: ${code}`);

  const conditionCode = materialKey.at(-1);
  const condition = { O: 'original', H: 'helper_2025', D: 'dftgen' }[conditionCode] || 'unknown';
  const stimulus = materialKey.slice(0, -1);

  return { code: normalized, stimulus, condition, reading_time_seconds: seconds };
}

const codes = process.argv.slice(2);
if (!codes.length) {
  console.error('Usage: node decode_completion_codes.js M-S1O-XXXX-YY [more codes...]');
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
