-- Copyright (c) 2026 Paul Butcher. All rights reserved.
-- Released under Apache 2.0 license as described in the file LICENSE.
module

public import CheckExampleGfm
meta import CheckExampleGfm

@[expose] public section

-- The C scanner advances past the first backslash even when the next
-- character terminates the domain scan.
#guard GFMarkdown.checkDomain true "a\\\\xb".toList == 2
#guard GFMarkdown.checkDomain true "a\\?b".toList == 2

-- A literal backslash followed by an underscore is examined by cmark-gfm's
-- domain scanner, so these candidates fail host validation.
#guard checkExampleGfm 1 "Backslash in autolink domain"
  "ftp://a\\x_b\n"
  "<p>ftp://a\\x_b</p>\n"

#guard checkExampleGfm 2 "Backslash in autolink domain"
  "http://foo\\x_bar.com\n"
  "<p>http://foo\\x_bar.com</p>\n"

#guard checkExampleGfm 3 "Backslash in autolink domain"
  "www.foo\\x_bar.com\n"
  "<p>www.foo\\x_bar.com</p>\n"

-- Backslash before underscore is resolved as a Markdown escape before autolinking.
#guard checkExampleGfm 4 "Escaped underscore"
  "http://a\\_b\n"
  "<p>http://a_b</p>\n"

-- The scanner still accepts a domain with no underscore after the skipped byte.
#guard checkExampleGfm 5 "Backslash without underscore"
  "http://a\\x.b\n"
  "<p><a href=\"http://a%5Cx.b\">http://a\\x.b</a></p>\n"

-- Retain the upstream guard for domains with more than ten dots.
#guard checkExampleGfm 6 "Long domain underscore"
  "http://a.b.c.d.e.f.g.h.i.j.k\\x_l.m\n"
  "<p><a href=\"http://a.b.c.d.e.f.g.h.i.j.k%5Cx_l.m\">http://a.b.c.d.e.f.g.h.i.j.k\\x_l.m</a></p>\n"
