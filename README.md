# Museum Materials Static Site

This folder is a pure static version for GitHub Pages.

URL format after deployment:

```text
https://<user-or-org>.github.io/<repo>/?stimulus=S1&condition=original&label=S1_original
https://<user-or-org>.github.io/<repo>/?stimulus=S1&condition=helper_2025&label=S1_helper_2025
https://<user-or-org>.github.io/<repo>/?stimulus=S1&condition=dftgen&label=S1_dftgen
https://<user-or-org>.github.io/<repo>/?stimulus=S2&condition=original&label=S2_original
https://<user-or-org>.github.io/<repo>/?stimulus=S2&condition=helper_2025&label=S2_helper_2025
https://<user-or-org>.github.io/<repo>/?stimulus=S2&condition=dftgen&label=S2_dftgen
```

No backend submission is used in this static version. The page starts a local hidden timer on load and only shows a completion code after the participant clicks "我已读完，生成完成码". For Credamo/JianShu, S1 and S2 are intended to be opened separately so each exhibit can have its own completion-code field.

Decode completion codes after export:

```bash
node decode_completion_codes.js OS1173
```

Completion code format: condition + stimulus + octal seconds. Example: `OS1173` means Original, S1, 123 seconds because octal `173` equals decimal `123`.
