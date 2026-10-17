#!/usr/bin/env python3
"""Compare Lean GFM extended-autolink rendering against cmark-gfm 0.29.0.gfm.13.

Run the Lean probe separately, saving stdout; this tool never modifies a repository.
"""
import argparse
import difflib
from pathlib import Path
import subprocess
import sys

# Keep sample names and Markdown input synchronized with GfmAutolinkDifferential.lean.
SAMPLES = [
    ("scheme-simple", "https://example.com\n"),
    ("www-simple", "www.example.com\n"),
    ("email-simple", "test@example.com\n"),
    ("scheme-underscore", "http://foo_xbar.com\n"),
    ("scheme-backslash-letter-underscore", "http://foo\\x_bar.com\n"),
    ("scheme-backslash-letter-period", "http://foo\\x.bar\n"),
    ("www-underscore", "www.foo_xbar.com\n"),
    ("www-backslash-letter-underscore", "www.foo\\x_bar.com\n"),
    ("www-backslash-letter-period", "www.foo\\x.bar\n"),
    ("scheme-escaped-period", "http://github\\.com\n"),
    ("www-escaped-period", "www.github\\.com\n"),
    ("scheme-escaped-colon", "http\\://github.com\n"),
    ("scheme-double-escaped-period", "http://github\\\\.com\n"),
    ("scheme-underscore-after-eleven-dots",
     "http://a.b.c.d.e.f.g.h.i.j.k.l_m.com\n"),
]


def parse_lean_output(text: str) -> dict[str, str]:
    lines = text.splitlines(keepends=True)
    result: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line.startswith("BEGIN_GFM_CASE:"):
            if line:
                raise ValueError(f"Unexpected Lean output: {line[:120]}")
            index += 1
            continue
        name = line.removeprefix("BEGIN_GFM_CASE:")
        if name in result:
            raise ValueError(f"Duplicate fixture: {name}")
        index += 1
        output = []
        closing = "END_GFM_CASE:" + name
        while index < len(lines) and lines[index].strip() != closing:
            output.append(lines[index])
            index += 1
        if index == len(lines):
            raise ValueError(f"Missing end marker for {name}")
        result[name] = "".join(output).rstrip("\n")
        index += 1
    expected = {name for name, _ in SAMPLES}
    if set(result) != expected:
        raise ValueError(f"Missing: {expected-set(result)}; extra: {set(result)-expected}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean-output", type=Path, required=True)
    parser.add_argument("--cmark", default="cmark-gfm")
    args = parser.parse_args()
    lean = parse_lean_output(args.lean_output.read_text(encoding="utf-8"))
    try:
        version = subprocess.run([args.cmark, "--version"], capture_output=True,
                                 text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Reference executable unavailable: {exc}", file=sys.stderr)
        return 2
    version_text = (version.stdout + version.stderr).strip()
    print("Reference:", version_text)
    if "0.29.0.gfm.13" not in version_text:
        print("Reference version differs from the pinned vendored version",
              file=sys.stderr)
        return 2
    mismatches = 0
    for name, sample in SAMPLES:
        process = subprocess.run([args.cmark, "-e", "autolink"], input=sample,
                                 capture_output=True, text=True, check=True)
        expected = process.stdout.rstrip("\n")
        actual = lean[name]
        matched = actual == expected
        print(f"{'MATCH' if matched else 'DIFFER':6} {name}")
        if not matched:
            mismatches += 1
            print("".join(difflib.unified_diff(
                [line + "\n" for line in expected.splitlines()],
                [line + "\n" for line in actual.splitlines()],
                fromfile="cmark-gfm", tofile="lean-gfm")).rstrip())
    print(f"Compared {len(SAMPLES)} cases; {mismatches} differences")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
