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

No backend submission is used in this static version. The page starts a local hidden timer on load and shows the reading time only after the participant clicks "我已读完". For Credamo/JianShu, S1 and S2 are intended to be opened separately so each exhibit can have its own reading-time record.
