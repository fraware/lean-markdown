/-
Copyright (c) 2026 Paul Butcher. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
-/
import GFMarkdown

open GFMarkdown

-- Characterization probes, not assertions of equivalence to cmark-gfm.
-- Each sample is one Markdown paragraph with one extended-autolink candidate.
private def autolinkSamples : List (String × String) := [
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
   "http://a.b.c.d.e.f.g.h.i.j.k.l_m.com\n")
]

#eval show IO Unit from do
  for (name, markdown) in autolinkSamples do
    IO.println ("BEGIN_GFM_CASE:" ++ name)
    IO.print (renderHtml (parseDocument markdown))
    IO.println ""
    IO.println ("END_GFM_CASE:" ++ name)
