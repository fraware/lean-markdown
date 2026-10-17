# GFM extended-autolink differential audit

This is an **investigation-only branch** based on `paulbutcher/lean-markdown` `f63d833bfd382bde0c85ae97edf336f83cff056a`. It changes no library or test code and is **not a proposed fix**.

## Question

The pinned reference, `github/cmark-gfm` tag `0.29.0.gfm.13`, uses `extensions/autolink.c` `check_domain`. Its loop skips the next input byte after a backslash and then continues accumulating underscores in the last two dot-delimited domain segments. See source lines 130-151.

`GFMarkdown/Autolink.lean` uses `checkDomainGo`, which stops at an invalid backslash. `matchSchemeWith` and `matchWww` subsequently append all non-whitespace text after that checked prefix. For inputs containing an uninterpreted Markdown backslash escape followed by an underscore, the two algorithms could disagree about whether to create an autolink.

Leading characterization candidates include `http://foo\x_bar.com` and `www.foo\x_bar.com` (a literal backslash followed by `x`, not an ASCII-punctuation escape). There are controls for ordinary underscores, escaped periods, and domains with more than ten dots, which exercise cmark-gfm's documented guard against expensive underscore-domain analysis.

The case `http://github\.com` also reproduces an example reported in upstream [cmark-gfm issue #388](https://github.com/github/cmark-gfm/issues/388). The reference implementation's behavior there is itself disputed. The purpose of the differential audit is **reference parity**, not independent judgment of ideal GFM syntax.

## Exact execution

Run using Lean 4.34.1 in an isolated clone/worktree of this branch:

```bash
set -euo pipefail
export PATH="$HOME/.elan/bin:$PATH"

lake build
lake env lean repros/GfmAutolinkDifferential.lean > /tmp/gfm-autolink-lean.txt

# cmark-gfm executable must report version 0.29.0.gfm.13.
cmark-gfm --version
python3 repros/compare_gfm_autolinks.py \
  --lean-output /tmp/gfm-autolink-lean.txt \
  --cmark cmark-gfm
```

The Python runner returns 0 for exact match, 1 for at least one difference, and 2 if the specified cmark-gfm reference is unavailable or has the wrong version. Exit 1 is an **investigative result**, not a passing conformance test. Keep the detailed side-by-side diffs.

If cmark-gfm is not installed, use an already available build or build the pinned upstream source in a disposable directory, with its native build instructions. Do not silently substitute a newer reference version or another Markdown library.

## Acceptance criteria for a real defect

1. Both implementations actually execute on the same input bytes, with pinned versions.
2. A minimized input produces an independent, reproducible difference in rendered HTML.
3. Explain the difference through parser/tokenization structure, including how Markdown treats the backslash, and identify the `GFMarkdown` source branch responsible.
4. Check that fixing the difference does not alter other escaping cases or reintroduce cmark-gfm's previously fixed underscore-domain quadratic attack.
5. Establish a red-before/green-after regression test, run `lake build`, `lake test`, and the existing GFM conformance guards.

Do not propose production code changes or upstream issues until those checks pass.

The probe and differential runner are intentionally excluded from root and test-project imports. This branch has no effect on downstream consumers.
