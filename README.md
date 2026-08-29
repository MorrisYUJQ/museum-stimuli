# British Museum Reading Materials Static Site

This folder is a pure static version for GitHub Pages. The deployed version contains two longer English British Museum exhibit texts and ten English comprehension questions.

URL format after deployment:

```text
https://<user-or-org>.github.io/<repo>/?stimulus=S1&condition=original&label=S1_original
https://<user-or-org>.github.io/<repo>/?stimulus=S1&condition=helper_2025&label=S1_helper_2025
https://<user-or-org>.github.io/<repo>/?stimulus=S1&condition=dftgen&label=S1_dftgen
https://<user-or-org>.github.io/<repo>/?stimulus=S2&condition=original&label=S2_original
https://<user-or-org>.github.io/<repo>/?stimulus=S2&condition=helper_2025&label=S2_helper_2025
https://<user-or-org>.github.io/<repo>/?stimulus=S2&condition=dftgen&label=S2_dftgen
```

No backend submission is used in this static version. The page starts a local hidden timer on load and only shows a completion code after the participant clicks "I have finished reading". For Credamo/JianShu, S1 and S2 are intended to be opened separately so each exhibit can have its own completion-code field.

The DFT-GEN condition provides adjustable font size, line spacing, letter spacing, word spacing, and an optional focus mask. Its completion code retains the original condition/stimulus/time prefix and appends the final display settings plus interaction counts. Original and Dyslexia Helper codes keep the legacy format.

Current stimuli:

- S1: The Parthenon
- S2: The Gayer-Anderson Cat

The ten English multiple-choice comprehension questions are in `stimuli_web_en/questions.csv`.

DFT-GEN workflow appendix page:

```text
https://<user-or-org>.github.io/<repo>/dftgen-workflow.html
```

Decode completion codes after export:

```bash
node decode_completion_codes.js OS1173
```

Completion code format: condition + stimulus + octal seconds. Example: `OS1173` means Original, S1, 123 seconds because octal `173` equals decimal `123`. A DFT-GEN code may include an optional telemetry suffix, for example `DS1173-F20L240A020W000X1100E1M1C3R0`. Run `decode_completion_codes.js` to split either format into analysis columns.
