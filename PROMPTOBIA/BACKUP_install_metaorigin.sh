#!/usr/bin/env bash
# MetaOrigin backup installer: creates the whole project, then tests, builds the .deb and APT repo.
# Usage: bash install_metaorigin.sh [--no-run]   (offline; Python 3 standard library only)
set -euo pipefail
ask() { local v="${!1:-}"; while [ -z "$v" ]; do read -r -p "$2: " v; done; printf -v "$1" %s "$v"; }
echo "MetaOrigin installer: answer 6 questions (used for About, LICENSE, README, package maintainer and URLs)."
ask NAME "1. Creator name"; ask EMAIL "2. Email"; ask DESIGNATION "3. Designation"; ask COMPANY "4. Company"
ask GHUSER "5. GitHub username"; ask GHREPO "6. GitHub repository name (the blank repo)"
export NAME EMAIL DESIGNATION COMPANY GHUSER GHREPO
DEST="${DEST:-$PWD/metaorigin}"; mkdir -p "$DEST"; cd "$DEST"
mkdir -p src packaging scripts tests docs samples dist build
cat > 'README.md' <<'MO_EOF_00'
# MetaOrigin

Check a file's metadata, get its MD5 sum, and see whether it looks edited or original.
Pure Python 3 standard library, works offline. Author: @@NAME@@, @@DESIGNATION@@, @@COMPANY@@ (@@EMAIL@@).

## Use

```
metaorigin FILE [FILE...]        full report (metadata, MD5, SHA-256, verdict)
metaorigin --md5 FILE            md5sum style line
metaorigin --json FILE           machine-readable report
metaorigin --verify HASH FILE    compare with a trusted MD5 or SHA-256 (exit 1 on mismatch)
metaorigin --about               author information
metaorigin-gui                   KDE dialog front end (needs kdialog)
```

Exit codes: 0 no indicators, 1 edit indicators or hash mismatch, 2 error.

## How the verdict works

Each file type is read for edit indicators: image editor names, XMP history, appended data (PNG, JPEG),
incremental updates and ModDate later than CreationDate (PDF), revision numbers, last-modified-by and
tracked changes (Word, Excel, PowerPoint, OpenDocument), and extension versus content mismatches.
Score 3 or more: LIKELY EDITED. 1 or 2: POSSIBLY EDITED. 0 with metadata: NO EDIT INDICATORS FOUND.
0 without metadata: INCONCLUSIVE.

This is a heuristic. Metadata can be stripped or forged. The only proof that a file is unchanged
is a match with a trusted hash (`--verify`).

## Install from the APT repository

```
sudo install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://@@GHUSER@@.github.io/@@GHREPO@@/apt/metaorigin.gpg | sudo tee /etc/apt/keyrings/metaorigin.gpg >/dev/null
printf 'Types: deb\nURIs: https://@@GHUSER@@.github.io/@@GHREPO@@/apt\nSuites: stable\nComponents: main\nSigned-By: /etc/apt/keyrings/metaorigin.gpg\n' | sudo tee /etc/apt/sources.list.d/metaorigin.sources
sudo apt update && sudo apt install metaorigin
```

Or download the .deb from the Releases page and run `sudo apt install ./metaorigin_1.0_all.deb`.

## Build, test and release (offline)

```
bash scripts/bootstrap.sh
bash tests/run_tests.sh
bash scripts/build_deb.sh
bash scripts/make_apt_repo.sh
bash scripts/check_apt_local.sh
bash scripts/git_init.sh https://github.com/@@GHUSER@@/@@GHREPO@@.git
bash scripts/release_v1.sh
```

Then in the browser: push with `git push -u origin main --tags`, publish the release (Releases, Draft a new
release, tag v1.0), and turn on Pages (Settings, Pages, Deploy from a branch, main, /docs).

Licensed under MIT. Copyright (c) @@YEAR@@ @@NAME@@.
MO_EOF_00
chmod 644 'README.md'
cat > 'LICENSE' <<'MO_EOF_01'
MIT License

Copyright (c) @@YEAR@@ @@NAME@@

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of
the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
MO_EOF_01
chmod 644 'LICENSE'
cat > 'CHANGELOG.md' <<'MO_EOF_02'
# Changelog

## V1.0
- First release: metadata report, MD5 and SHA-256, edit indicators, KDE dialog, .deb and APT repository.
MO_EOF_02
chmod 644 'CHANGELOG.md'
cat > '.gitignore' <<'MO_EOF_03'
build/
dist/
__pycache__/
*.pyc
.gnupg/
MO_EOF_03
chmod 644 '.gitignore'
cat > 'src/metaorigin.py' <<'MO_EOF_04'
#!/usr/bin/env python3
"""MetaOrigin: file metadata, MD5 and a heuristic edited-or-original check."""
import argparse, datetime as dt, hashlib, json, os, re, signal, struct, subprocess, sys, zipfile, zlib
from xml.etree import ElementTree as ET

VERSION = "1.0"
MAX_PARSE = 64 * 1024 * 1024
EDITORS = ("photoshop", "lightroom", "gimp", "paint.net", "pixlr", "snapseed", "canva", "affinity",
           "picsart", "facetune", "luminar", "capture one", "acdsee", "photoscape", "fotor", "krita")
PDF_TOOLS = ("pdf editor", "pdfescape", "sejda", "ilovepdf", "smallpdf", "foxit", "pdf-xchange",
             "nitro", "pdfelement", "pdffiller", "pikepdf", "pypdf", "pdftk", "itext", "acrobat")
MAGIC = [(b"\x89PNG\r\n\x1a\n", "png"), (b"\xff\xd8\xff", "jpg"), (b"%PDF-", "pdf"), (b"GIF8", "gif"),
         (b"PK\x03\x04", "zip"), (b"BM", "bmp"), (b"\x7fELF", "elf"), (b"MZ", "exe"), (b"ID3", "mp3"),
         (b"\x1f\x8b", "gz")]
EXT = {"jpg": "jpg", "jpeg": "jpg", "png": "png", "pdf": "pdf", "gif": "gif", "docx": "zip", "xlsx": "zip",
       "pptx": "zip", "odt": "zip", "ods": "zip", "odp": "zip", "zip": "zip", "bmp": "bmp", "exe": "exe",
       "mp3": "mp3", "gz": "gz"}
NOTE = ("Heuristic only: metadata can be stripped or forged. The only proof a file is unchanged is a match "
        "with a trusted hash (use --verify).")


def iso(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def hashes(path):
    m, s = hashlib.md5(usedforsecurity=False), hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            m.update(chunk); s.update(chunk)
    return m.hexdigest(), s.hexdigest()


def pdt(s):
    """Parse EXIF, PDF or ISO date text into a naive UTC datetime, or None."""
    if not s:
        return None
    s = s.strip()
    m = re.match(r"D:(\d{4})(\d\d)(\d\d)(\d\d)?(\d\d)?(\d\d)?", s)
    if not m:
        m = re.match(r"(\d{4})[-:](\d\d)[-:](\d\d)[T ](\d\d):(\d\d):(\d\d)", s)
    if not m:
        return None
    try:
        return dt.datetime(*[int(x) if x else 0 for x in m.groups()])
    except ValueError:
        return None


def gap(a, b):
    a, b = pdt(a), pdt(b)
    return abs((b - a).total_seconds()) if a and b else 0


class Ev:
    def __init__(self):
        self.items, self.meta = [], {}

    def add(self, pts, text):
        self.items.append((pts, text))

    @property
    def score(self):
        return sum(p for p, _ in self.items)


def detect(d, name):
    kind = next((k for sig, k in MAGIC if d.startswith(sig)), None)
    if kind == "zip":
        try:
            z = zipfile.ZipFile(name)
            names = z.namelist()
            if "[Content_Types].xml" in names:
                kind = "ooxml"
            elif "mimetype" in names and z.read("mimetype").startswith(b"application/vnd.oasis"):
                kind = "odf"
        except Exception:
            pass
    return kind


def exif(t, ev, size):
    e = "<" if t[:2] == b"II" else ">"
    names = {0x10F: "Make", 0x110: "Model", 0x131: "Software", 0x132: "DateTime", 0x13B: "Artist",
             0x9003: "DateTimeOriginal", 0x9004: "DateTimeDigitized", 0xA002: "ExifWidth", 0xA003: "ExifHeight"}

    def ifd(off):
        out = {}
        n = struct.unpack(e + "H", t[off:off + 2])[0]
        for i in range(n):
            tag, typ, cnt, val = struct.unpack(e + "HHII", t[off + 2 + i * 12:off + 14 + i * 12])
            if typ == 2:
                raw = t[val:val + cnt] if cnt > 4 else t[off + 10 + i * 12:off + 10 + i * 12 + cnt]
                out[tag] = raw.split(b"\0")[0].decode("latin1")
            elif typ == 3 and cnt == 1:
                out[tag] = struct.unpack(e + "H", t[off + 10 + i * 12:off + 12 + i * 12])[0]
            elif typ == 4 and cnt == 1:
                out[tag] = val
        return out
    try:
        a = ifd(struct.unpack(e + "I", t[4:8])[0])
        if 0x8769 in a:
            a.update(ifd(a[0x8769]))
    except Exception:
        return
    for tag, nm in names.items():
        if tag in a:
            ev.meta["EXIF " + nm] = a[tag]
    sw = str(a.get(0x131, "")).lower()
    if any(x in sw for x in EDITORS):
        ev.add(3, "EXIF Software names an image editor: " + a[0x131])
    if gap(a.get(0x9003), a.get(0x132)) > 2:
        ev.add(2, "EXIF DateTime differs from DateTimeOriginal")
    if a.get(0xA002) and size and (a[0xA002], a.get(0xA003)) != size:
        ev.add(2, "EXIF dimensions differ from the real image size")


def jpg(d, ev):
    pos, size = 2, None
    while pos + 4 <= len(d) and d[pos] == 0xFF:
        m = d[pos + 1]
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            pos += 2; continue
        if m == 0xD9:
            break
        ln = struct.unpack(">H", d[pos + 2:pos + 4])[0]
        seg = d[pos + 4:pos + 2 + ln]
        if m == 0xE1 and seg.startswith(b"Exif\0\0"):
            pending = seg[6:]
        elif m == 0xE1 and seg.startswith(b"http://ns.adobe.com/xap/1.0/"):
            ev.meta["XMP"] = "present"
            if re.search(rb"History|DerivedFrom|photoshop:", seg):
                ev.add(3, "XMP records an editing history")
        elif 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", seg[1:5]); size = (w, h)
            ev.meta["Image size"] = "%dx%d" % size
        if m == 0xDA:
            break
        pos += 2 + ln
    for m in re.finditer(rb"\xff\xe1", d[:65536]):
        seg = d[m.start() + 4:m.start() + 4 + 20]
        if seg.startswith(b"Exif\0\0"):
            ln = struct.unpack(">H", d[m.start() + 2:m.start() + 4])[0]
            exif(d[m.start() + 10:m.start() + 2 + ln], ev, size); break
    else:
        ev.meta.setdefault("EXIF", "absent")
    end = d.rfind(b"\xff\xd9")
    if end != -1 and len(d) - (end + 2) > 0:
        ev.add(1, "Extra bytes after the JPEG end marker")


def png(d, ev):
    pos, end = 8, None
    while pos + 12 <= len(d):
        ln, typ = struct.unpack(">I4s", d[pos:pos + 8])
        body = d[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            ev.meta["Image size"] = "%dx%d" % struct.unpack(">II", body[:8])
        elif typ == b"tEXt":
            k, _, v = body.partition(b"\0")
            k, v = k.decode("latin1"), v.decode("latin1")
            ev.meta["PNG " + k] = v
            if k.lower() == "software" and any(x in v.lower() for x in EDITORS):
                ev.add(3, "Software field names an image editor: " + v)
        elif typ == b"iTXt":
            k, _, rest = body.partition(b"\0")
            comp = rest[0]; rest = rest[2:]
            _, _, rest = rest.partition(b"\0"); _, _, text = rest.partition(b"\0")
            if comp:
                text = zlib.decompress(text)
            if k == b"XML:com.adobe.xmp":
                ev.meta["XMP"] = "present"
                if re.search(rb"History|DerivedFrom|photoshop:", text):
                    ev.add(3, "XMP records an editing history")
        elif typ == b"tIME":
            y, mo, da, h, mi, s = struct.unpack(">HBBBBB", body)
            ev.meta["PNG last-modified chunk"] = "%04d-%02d-%02d %02d:%02d:%02d" % (y, mo, da, h, mi, s)
            ev.add(1, "PNG tIME chunk records a modification time")
        pos += 12 + ln
        if typ == b"IEND":
            end = pos; break
    if end and len(d) - end > 0:
        ev.add(2, "%d byte(s) appended after the PNG end chunk" % (len(d) - end))


def pdf(d, ev):
    eofs = len(re.findall(rb"%%EOF", d))
    updates = eofs - (2 if b"/Linearized" in d[:2048] else 1)
    ev.meta["PDF version"] = d[5:8].decode("latin1")
    info = {}
    for m in re.finditer(rb"/(Producer|Creator|CreationDate|ModDate|Title|Author)\s*\(((?:[^()\\]|\\.)*)\)", d):
        info[m.group(1).decode()] = m.group(2).decode("latin1")
    ev.meta.update({"PDF " + k: v for k, v in info.items()})
    if updates > 0:
        ev.add(3, "PDF has %d incremental update(s) after first save" % updates)
    if gap(info.get("CreationDate"), info.get("ModDate")) > 60:
        ev.add(2, "ModDate is later than CreationDate")
    tool = (info.get("Producer", "") + " " + info.get("Creator", "")).lower()
    if any(x in tool for x in PDF_TOOLS):
        ev.add(1, "Producer or Creator names an editing or post-processing tool")


def xmltext(z, name):
    try:
        root = ET.fromstring(z.read(name))
    except Exception:
        return {}
    return {el.tag.split("}")[-1]: (el.text or "").strip() for el in root.iter() if (el.text or "").strip()}


def ooxml(path, ev):
    z = zipfile.ZipFile(path)
    core, app = xmltext(z, "docProps/core.xml"), xmltext(z, "docProps/app.xml")
    for k in ("creator", "lastModifiedBy", "created", "modified", "revision"):
        if k in core:
            ev.meta["Office " + k] = core[k]
    for k in ("Application", "AppVersion", "TotalTime"):
        if k in app:
            ev.meta["Office " + k] = app[k]
    if core.get("revision", "1").isdigit() and int(core.get("revision", "1")) > 1:
        ev.add(2, "Revision number is %s" % core["revision"])
    if gap(core.get("created"), core.get("modified")) > 60:
        ev.add(2, "Modified time is later than created time")
    a, b = core.get("creator"), core.get("lastModifiedBy")
    if a and b and a != b:
        ev.add(2, "Last modified by a different person than the creator")
    if app.get("TotalTime", "0").isdigit() and int(app["TotalTime"]) > 0:
        ev.add(1, "Editing time of %s minute(s) recorded" % app["TotalTime"])
    names = z.namelist()
    if "word/document.xml" in names:
        x = z.read("word/document.xml")
        if b"<w:ins " in x or b"<w:del " in x:
            ev.add(3, "Tracked insertions or deletions are present")
    if any(n.endswith("comments.xml") for n in names):
        ev.add(1, "Comments part is present")


def odf(path, ev):
    z = zipfile.ZipFile(path)
    m = xmltext(z, "meta.xml")
    for k in ("generator", "initial-creator", "creator", "creation-date", "date", "editing-cycles"):
        if k in m:
            ev.meta["ODF " + k] = m[k]
    if m.get("editing-cycles", "1").isdigit() and int(m.get("editing-cycles", "1")) > 1:
        ev.add(2, "Editing cycles: %s" % m["editing-cycles"])
    if gap(m.get("creation-date"), m.get("date")) > 60:
        ev.add(2, "Last-saved time is later than creation time")
    if m.get("initial-creator") and m.get("creator") and m["initial-creator"] != m["creator"]:
        ev.add(2, "Last editor differs from the initial creator")


def analyze(path):
    st = os.stat(path)
    md5, sha = hashes(path)
    r = {"file": path, "size": st.st_size, "md5": md5, "sha256": sha,
         "modified": iso(st.st_mtime), "accessed": iso(st.st_atime), "status_changed": iso(st.st_ctime)}
    try:
        b = subprocess.run(["stat", "-c", "%W", path], capture_output=True, text=True, timeout=3).stdout.strip()
        if b.isdigit() and int(b) > 0:
            r["created"] = iso(int(b))
    except Exception:
        pass
    ev = Ev()
    if st.st_mtime > dt.datetime.now().timestamp() + 86400:
        ev.add(1, "File modified time is in the future")
    if st.st_size == 0:
        r.update(type="empty", verdict="INCONCLUSIVE", score=0, evidence=[], metadata={}, note=NOTE)
        return r
    with open(path, "rb") as f:
        d = f.read(MAX_PARSE)
    kind = detect(d, path)
    r["type"] = kind or "unknown/text"
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    claimed = EXT.get(ext)
    if kind and claimed and claimed != ("zip" if kind in ("ooxml", "odf") else kind):
        ev.add(2, "Extension .%s does not match the content (%s)" % (ext, kind))
    try:
        if st.st_size > MAX_PARSE:
            ev.meta["Note"] = "Large file: metadata check skipped, hashes only"
        elif kind == "jpg": jpg(d, ev)
        elif kind == "png": png(d, ev)
        elif kind == "pdf": pdf(d, ev)
        elif kind == "ooxml": ooxml(path, ev)
        elif kind == "odf": odf(path, ev)
    except Exception as exc:
        ev.meta["Parse note"] = "partial: %s" % type(exc).__name__
    has_meta = any(not k.startswith("Image size") and k != "Note" for k in ev.meta)
    if ev.score >= 3: v = "LIKELY EDITED"
    elif ev.score >= 1: v = "POSSIBLY EDITED"
    elif has_meta: v = "NO EDIT INDICATORS FOUND"
    else: v = "INCONCLUSIVE"
    r.update(verdict=v, score=ev.score, evidence=[{"points": p, "text": t} for p, t in ev.items],
             metadata=ev.meta, note=NOTE)
    return r


def show(r):
    out = ["File     : %s" % r["file"], "MD5      : %s" % r["md5"], "SHA-256  : %s" % r["sha256"],
           "Size     : %d bytes" % r["size"], "Type     : %s" % r["type"],
           "Modified : %s" % r["modified"], "Changed  : %s" % r["status_changed"],
           "Accessed : %s" % r["accessed"]]
    if "created" in r:
        out.append("Created  : %s" % r["created"])
    if "verify" in r:
        out.append("Verify   : %s" % r["verify"])
    out.append("Metadata :" + ("" if r["metadata"] else " none found"))
    out += ["  %s: %s" % kv for kv in r["metadata"].items()]
    out.append("Evidence :" + ("" if r["evidence"] else " none"))
    out += ["  [+%d] %s" % (e["points"], e["text"]) for e in r["evidence"]]
    out += ["VERDICT  : %s (score %d)" % (r["verdict"], r["score"]), "Note     : " + r["note"]]
    return "\n".join(out)


def main(argv=None):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    ap = argparse.ArgumentParser(prog="metaorigin", description="File metadata, MD5 and edited-or-original check.")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--md5", action="store_true", help="print only 'md5  path' lines")
    ap.add_argument("--verify", metavar="HASH", help="compare MD5 or SHA-256 with a trusted value")
    ap.add_argument("--about", action="store_true", help="show author information")
    ap.add_argument("--version", action="version", version="metaorigin " + VERSION)
    a = ap.parse_args(argv)
    here = os.path.dirname(os.path.abspath(__file__))
    if a.about:
        ab = json.load(open(os.path.join(here, "about.json")))
        print("%s %s\n%s\n\nAuthor     : %s\nDesignation: %s\nCompany    : %s\nEmail      : %s\nProject    : %s" % (
            ab["app"], ab["version"], ab["tagline"], ab["name"], ab["designation"], ab["company"], ab["email"], ab["homepage"]))
        return 0
    if not a.files:
        ap.print_usage(sys.stderr); return 2
    results, code = [], 0
    for p in a.files:
        try:
            r = analyze(p)
        except OSError as exc:
            print("metaorigin: %s: %s" % (p, exc.strerror), file=sys.stderr); code = 2; continue
        if a.verify:
            want = a.verify.strip().lower()
            got = r["md5"] if len(want) == 32 else r["sha256"]
            r["verify"] = "MATCH" if got == want else "MISMATCH"
            if got != want: code = max(code, 1)
        elif r["verdict"] in ("LIKELY EDITED", "POSSIBLY EDITED"):
            code = max(code, 1)
        results.append(r)
    if a.md5:
        print("\n".join("%s  %s" % (r["md5"], r["file"]) for r in results))
    elif a.json:
        print(json.dumps(results if len(results) != 1 else results[0], indent=2))
    else:
        print("\n\n".join(show(r) for r in results))
    return code


if __name__ == "__main__":
    sys.exit(main())
MO_EOF_04
chmod 755 'src/metaorigin.py'
cat > 'src/about.json' <<'MO_EOF_05'
{"app":"MetaOrigin","version":"1.0","tagline":"Check metadata, MD5 and whether a file looks edited","name":"@@NAME@@","designation":"@@DESIGNATION@@","company":"@@COMPANY@@","email":"@@EMAIL@@","homepage":"https://github.com/@@GHUSER@@/@@GHREPO@@"}
MO_EOF_05
chmod 644 'src/about.json'
cat > 'packaging/metaorigin' <<'MO_EOF_06'
#!/bin/sh
exec python3 /usr/lib/metaorigin/metaorigin.py "$@"
MO_EOF_06
chmod 755 'packaging/metaorigin'
cat > 'packaging/metaorigin-gui' <<'MO_EOF_07'
#!/bin/bash
# Simple KDE dialog front end. Falls back to the terminal when kdialog is missing.
APP=/usr/lib/metaorigin/metaorigin.py
[ -f "$APP" ] || APP="$(dirname "$0")/../src/metaorigin.py"
if ! command -v kdialog >/dev/null 2>&1; then
  echo "kdialog not found. Usage: metaorigin FILE" >&2
  exec python3 "$APP" "$@"
fi
while true; do
  choice=$(kdialog --title "MetaOrigin" --menu "What would you like to do?" check "Check a file" about "About" quit "Quit") || exit 0
  case "$choice" in
    check)
      f=$(kdialog --title "Choose a file" --getopenfilename "$HOME") || continue
      out=$(mktemp); python3 "$APP" "$f" >"$out" 2>&1
      kdialog --title "MetaOrigin result" --textbox "$out" 780 560; rm -f "$out" ;;
    about)
      out=$(mktemp); python3 "$APP" --about >"$out" 2>&1
      kdialog --title "About MetaOrigin" --textbox "$out" 520 300; rm -f "$out" ;;
    *) exit 0 ;;
  esac
done
MO_EOF_07
chmod 755 'packaging/metaorigin-gui'
cat > 'packaging/metaorigin.desktop' <<'MO_EOF_08'
[Desktop Entry]
Type=Application
Name=MetaOrigin
GenericName=File metadata and origin check
Comment=Show file metadata, MD5 and whether a file looks edited
Exec=metaorigin-gui
Icon=metaorigin
Terminal=false
Categories=Utility;
Keywords=metadata;md5;forensics;exif;
MO_EOF_08
chmod 644 'packaging/metaorigin.desktop'
cat > 'packaging/metaorigin.svg' <<'MO_EOF_09'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#0A0E2A"/><rect x="14" y="10" width="30" height="40" rx="3" fill="#fff"/><path d="M20 22h18M20 30h18M20 38h10" stroke="#7C3AED" stroke-width="3" stroke-linecap="round"/><circle cx="44" cy="42" r="11" fill="none" stroke="#00F0FF" stroke-width="4"/><path d="M52 50l7 7" stroke="#00F0FF" stroke-width="4" stroke-linecap="round"/></svg>
MO_EOF_09
chmod 644 'packaging/metaorigin.svg'
cat > 'packaging/make_repo.py' <<'MO_EOF_10'
#!/usr/bin/env python3
"""Create a static APT repository (dists/ + pool/) with the standard library only."""
import datetime as dt, gzip, hashlib, os, shutil, subprocess, sys

deb, out = sys.argv[1], sys.argv[2]
ARCHS = ["amd64", "arm64", "all"]
ctl = subprocess.run(["dpkg-deb", "-f", deb], capture_output=True, text=True, check=True).stdout.rstrip("\n")
fields = dict(l.split(": ", 1) for l in ctl.splitlines() if not l.startswith(" ") and ": " in l)
name = fields["Package"]
rel = "pool/main/%s/%s/%s" % (name[0], name, os.path.basename(deb))
os.makedirs(os.path.join(out, os.path.dirname(rel)), exist_ok=True)
shutil.copy(deb, os.path.join(out, rel))
data = open(deb, "rb").read()
stanza = ctl + "\nFilename: %s\nSize: %d\nMD5sum: %s\nSHA256: %s\n" % (
    rel, len(data), hashlib.md5(data, usedforsecurity=False).hexdigest(), hashlib.sha256(data).hexdigest())
files = []
for a in ARCHS:
    d = os.path.join(out, "dists/stable/main/binary-" + a)
    os.makedirs(d, exist_ok=True)
    raw = stanza.encode()
    open(os.path.join(d, "Packages"), "wb").write(raw)
    gz = gzip.compress(raw, 9, mtime=0)
    open(os.path.join(d, "Packages.gz"), "wb").write(gz)
    files += [("main/binary-%s/Packages" % a, raw), ("main/binary-%s/Packages.gz" % a, gz)]
now = dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")
lines = ["Origin: %s" % name, "Label: %s" % name, "Suite: stable", "Codename: stable", "Date: " + now,
         "Architectures: " + " ".join(ARCHS), "Components: main", "Description: %s APT repository" % name]
for title, fn in (("MD5Sum", lambda b: hashlib.md5(b, usedforsecurity=False)), ("SHA256", hashlib.sha256)):
    lines.append(title + ":")
    lines += [" %s %16d %s" % (fn(b).hexdigest(), len(b), p) for p, b in files]
open(os.path.join(out, "dists/stable/Release"), "w").write("\n".join(lines) + "\n")
print("Repository written to", out)
MO_EOF_10
chmod 755 'packaging/make_repo.py'
cat > 'scripts/bootstrap.sh' <<'MO_EOF_11'
#!/usr/bin/env bash
# Create the folder tree and sample files. Safe to run more than once.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p src packaging scripts tests docs samples dist build
chmod +x scripts/*.sh tests/*.sh packaging/metaorigin packaging/metaorigin-gui packaging/make_repo.py 2>/dev/null || true
python3 tests/make_samples.py samples
echo "Project folders ready."
MO_EOF_11
chmod 755 'scripts/bootstrap.sh'
cat > 'scripts/build_deb.sh' <<'MO_EOF_12'
#!/usr/bin/env bash
# Build dist/metaorigin_<version>_all.deb using only dpkg-deb (no internet needed).
set -euo pipefail
cd "$(dirname "$0")/.."
IFS=$'\t' read -r VER NAME EMAIL HOME_URL < <(python3 -c "import json;a=json.load(open('src/about.json'));print('\t'.join([a['version'],a['name'],a['email'],a['homepage']]))")
PKG=metaorigin; ROOT="build/${PKG}_${VER}_all"
rm -rf build "dist/${PKG}_${VER}_all.deb"; mkdir -p dist
install -d -m 0755 "$ROOT/DEBIAN" "$ROOT/usr/bin" "$ROOT/usr/lib/$PKG" "$ROOT/usr/share/applications" \
  "$ROOT/usr/share/icons/hicolor/scalable/apps" "$ROOT/usr/share/doc/$PKG"
install -m 0644 src/metaorigin.py src/about.json "$ROOT/usr/lib/$PKG/"
install -m 0755 packaging/metaorigin packaging/metaorigin-gui "$ROOT/usr/bin/"
install -m 0644 packaging/metaorigin.desktop "$ROOT/usr/share/applications/"
install -m 0644 packaging/metaorigin.svg "$ROOT/usr/share/icons/hicolor/scalable/apps/"
install -m 0644 README.md "$ROOT/usr/share/doc/$PKG/README.md"
printf 'MetaOrigin %s\nCopyright (c) %s %s\nLicense: MIT\n' "$VER" "$(date +%Y)" "$NAME" > "$ROOT/usr/share/doc/$PKG/copyright"
cat > "$ROOT/DEBIAN/control" <<CTL
Package: $PKG
Version: $VER
Section: utils
Priority: optional
Architecture: all
Depends: python3 (>= 3.10)
Recommends: kdialog
Maintainer: $NAME <$EMAIL>
Homepage: $HOME_URL
Description: Check file metadata, MD5 and whether a file looks edited
 MetaOrigin reads the metadata of images, PDF, Office and OpenDocument files,
 prints the MD5 sum and reports edit indicators. The verdict is a heuristic.
CTL
dpkg-deb --root-owner-group -Zxz --build "$ROOT" "dist/${PKG}_${VER}_all.deb" >/dev/null
echo "Built dist/${PKG}_${VER}_all.deb"
dpkg-deb --info "dist/${PKG}_${VER}_all.deb" >/dev/null
MO_EOF_12
chmod 755 'scripts/build_deb.sh'
cat > 'scripts/make_apt_repo.sh' <<'MO_EOF_13'
#!/usr/bin/env bash
# Build docs/apt (static APT repo for GitHub Pages) and sign it when gpg is available.
set -euo pipefail
cd "$(dirname "$0")/.."
DEB=$(ls -1 dist/metaorigin_*_all.deb | tail -1)
rm -rf docs/apt; python3 packaging/make_repo.py "$DEB" docs/apt
export GNUPGHOME="${GNUPGHOME:-$HOME/.local/share/metaorigin-gnupg}"
if command -v gpg >/dev/null 2>&1; then
  if [ ! -d "$GNUPGHOME" ]; then
    mkdir -p "$GNUPGHOME"; chmod 700 "$GNUPGHOME"
    IFS=$'\t' read -r NAME EMAIL < <(python3 -c "import json;a=json.load(open('src/about.json'));print(a['name']+'\t'+a['email'])")
    gpg --batch --pinentry-mode loopback --passphrase '' --quick-generate-key "$NAME (MetaOrigin APT) <$EMAIL>" ed25519 sign never
  fi
  R=docs/apt/dists/stable
  gpg --batch --yes --armor --detach-sign -o "$R/Release.gpg" "$R/Release"
  gpg --batch --yes --clearsign -o "$R/InRelease" "$R/Release"
  gpg --batch --yes --export -o docs/apt/metaorigin.gpg
  gpg --batch --yes --armor --export -o docs/apt/metaorigin.asc
  echo "Signed repository. Public key: docs/apt/metaorigin.gpg"
else
  echo "gpg not found: repository is unsigned (clients need [trusted=yes])"
fi
touch docs/.nojekyll
MO_EOF_13
chmod 755 'scripts/make_apt_repo.sh'
cat > 'scripts/git_init.sh' <<'MO_EOF_14'
#!/usr/bin/env bash
# Initialise git with the author's identity (repository-local) and optionally add the remote.
set -euo pipefail
cd "$(dirname "$0")/.."
IFS=$'\t' read -r NAME EMAIL < <(python3 -c "import json;a=json.load(open('src/about.json'));print(a['name']+'\t'+a['email'])")
[ -d .git ] || git init -q -b main
git config user.name "$NAME"; git config user.email "$EMAIL"
[ -n "${1:-}" ] && { git remote remove origin 2>/dev/null || true; git remote add origin "$1"; }
git add -A && git commit -q -m "MetaOrigin V1.0" && echo "Committed. Remote: $(git remote get-url origin 2>/dev/null || echo none)"
MO_EOF_14
chmod 755 'scripts/git_init.sh'
cat > 'scripts/release_v1.sh' <<'MO_EOF_15'
#!/usr/bin/env bash
# Prepare release files for V1.0 (no GitHub CLI). Run after: bash tests/run_tests.sh && bash scripts/build_deb.sh
set -euo pipefail
cd "$(dirname "$0")/.."
VER=$(python3 -c "import json;print(json.load(open('src/about.json'))['version'])")
git rev-parse --git-dir >/dev/null 2>&1 || { echo "Run scripts/git_init.sh first"; exit 1; }
git diff --quiet && git diff --cached --quiet || { echo "Commit your changes first (git add -A && git commit)"; exit 1; }
rm -f dist/*.tar.gz dist/SHA256SUMS dist/MD5SUMS
git archive --format=tar.gz --prefix="metaorigin-$VER/" -o "dist/metaorigin-$VER-src.tar.gz" HEAD
( cd dist && sha256sum metaorigin_*_all.deb metaorigin-*-src.tar.gz > SHA256SUMS && md5sum metaorigin_*_all.deb metaorigin-*-src.tar.gz > MD5SUMS )
git rev-parse "v$VER" >/dev/null 2>&1 || git tag -a "v$VER" -m "MetaOrigin V$VER"
echo "Tag v$VER ready. Files to attach on the GitHub release page:"; ls -1 dist/
cat <<MSG

Next (browser): push with  git push origin main --tags
Then GitHub > Releases > Draft a new release > choose tag v$VER > title "V$VER"
Attach: dist/metaorigin_${VER}_all.deb, dist/metaorigin-$VER-src.tar.gz, dist/SHA256SUMS, dist/MD5SUMS > Publish release.
MSG
MO_EOF_15
chmod 755 'scripts/release_v1.sh'
cat > 'scripts/demo.sh' <<'MO_EOF_16'
#!/usr/bin/env bash
# Live demo: original versus edited files, then MD5 and --verify.
set -uo pipefail
cd "$(dirname "$0")/.."
[ -d samples ] && [ -f samples/original.png ] || bash scripts/bootstrap.sh >/dev/null
for f in original.pdf edited.pdf original.docx edited.docx original.png edited.png renamed.jpg notes.txt; do
  printf '\n=== %s ===\n' "$f"; python3 src/metaorigin.py "samples/$f" | grep -E '^(MD5|Type|Evidence|  \[|VERDICT)'
done
printf '\n=== MD5 and verify ===\n'
h=$(md5sum samples/notes.txt | cut -d' ' -f1)
python3 src/metaorigin.py --verify "$h" samples/notes.txt | grep -E '^(MD5|Verify)'
MO_EOF_16
chmod 755 'scripts/demo.sh'
cat > 'scripts/check_apt_local.sh' <<'MO_EOF_17'
#!/usr/bin/env bash
# Prove the APT repo works: serve docs/ on localhost and let real apt read it (no root, no internet).
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d); PORT=$((20000 + RANDOM % 20000))
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory docs >/dev/null 2>&1 &
SRV=$!; trap 'kill $SRV 2>/dev/null || true; rm -rf "$T"' EXIT
mkdir -p "$T/state/lists/partial" "$T/cache/archives/partial" "$T/dl"; sleep 1
if [ -f docs/apt/metaorigin.gpg ]; then
  cp docs/apt/metaorigin.gpg "$T/key.gpg"; OPT="signed-by=$T/key.gpg"
else OPT="trusted=yes"; fi
echo "deb [$OPT] http://127.0.0.1:$PORT/apt stable main" > "$T/s.list"
A=(-o "Dir::Etc::sourcelist=$T/s.list" -o "Dir::Etc::sourceparts=/dev/null" -o "Dir::State=$T/state" -o "Dir::Cache=$T/cache" -o "Debug::NoLocking=1" -o "APT::Sandbox::User=$(id -un)")
apt-get "${A[@]}" update
apt-cache "${A[@]}" policy metaorigin
( cd "$T/dl" && apt-get "${A[@]}" download metaorigin && ls -l ./*.deb )
echo "APT repository check: OK"
MO_EOF_17
chmod 755 'scripts/check_apt_local.sh'
cat > 'tests/make_samples.py' <<'MO_EOF_18'
#!/usr/bin/env python3
"""Create small sample files (original vs edited) using only the standard library."""
import os, struct, sys, zipfile, zlib

OUT = sys.argv[1] if len(sys.argv) > 1 else "samples"
os.makedirs(OUT, exist_ok=True)


def chunk(t, body):
    return struct.pack(">I", len(body)) + t + body + struct.pack(">I", zlib.crc32(t + body) & 0xFFFFFFFF)


def png(extra=()):
    rows = b"".join(b"\0" + bytes(v for x in range(8) for v in (x * 32, y * 32, 128)) for y in range(8))
    out = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 8, 8, 8, 2, 0, 0, 0))
    for t, b in extra:
        out += chunk(t, b)
    return out + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


def pdf(info, update=None):
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] >>", info]
    out, offs = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offs.append(len(out)); out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    x = len(out)
    out += b"xref\n0 5\n0000000000 65535 f \n" + b"".join(b"%010d 00000 n \n" % o for o in offs)
    out += b"trailer\n<< /Size 5 /Root 1 0 R /Info 4 0 R >>\nstartxref\n%d\n%%%%EOF\n" % x
    if update:
        o4 = len(out)
        out += b"4 0 obj\n" + update + b"\nendobj\n"
        x2 = len(out)
        out += b"xref\n4 1\n%010d 00000 n \n" % o4
        out += b"trailer\n<< /Size 5 /Root 1 0 R /Info 4 0 R /Prev %d >>\nstartxref\n%d\n%%%%EOF\n" % (x, x2)
    return out


def docx(path, core, body):
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
          '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '</Relationships>')
    doc = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:body>' + body + '</w:body></w:document>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc); z.writestr("docProps/core.xml", core)


def core(creator, last, created, modified, rev):
    return ('<?xml version="1.0" encoding="UTF-8"?><cp:coreProperties '
            'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dc:creator>%s</dc:creator><cp:lastModifiedBy>%s</cp:lastModifiedBy><cp:revision>%d</cp:revision>'
            '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
            '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified></cp:coreProperties>'
            % (creator, last, rev, created, modified))


def jpeg(entries, trailer=b""):
    """Marker-only JPEG used to test EXIF reading; it is not a viewable picture."""
    e = "<"
    def ascii_(t, s):
        return (t, 2, s.encode() + b"\0")
    items = [ascii_(*x) for x in entries]
    ifd_len = 2 + 12 * len(items) + 4
    data, ents, off = b"", b"", 8 + ifd_len
    for tag, typ, val in items:
        if len(val) <= 4:
            ents += struct.pack(e + "HHI", tag, typ, len(val)) + val.ljust(4, b"\0")
        else:
            ents += struct.pack(e + "HHII", tag, typ, len(val), off + len(data)); data += val
    tiff = b"II*\0" + struct.pack(e + "I", 8) + struct.pack(e + "H", len(items)) + ents + b"\0\0\0\0" + data
    app1 = b"Exif\0\0" + tiff
    sof = b"\x08" + struct.pack(">HH", 8, 8) + b"\x01\x01\x11\x00"
    return (b"\xff\xd8\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1 + b"\xff\xc0" +
            struct.pack(">H", len(sof) + 2) + sof + b"\xff\xda\x00\x02\xff\xd9" + trailer)


def w(name, data):
    with open(os.path.join(OUT, name), "wb") as f:
        f.write(data)


xmp = (b"XML:com.adobe.xmp\0\0\0\0\0" + b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
       b'<rdf:Description xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/"><xmpMM:History><rdf:Seq/></xmpMM:History></rdf:Description></rdf:RDF></x:xmpmeta>')
w("original.png", png([(b"tEXt", b"Comment\0Sample original image"), (b"tEXt", b"Title\0Original sample")]))
w("edited.png", png([(b"tEXt", b"Software\0Adobe Photoshop 25.0"), (b"iTXt", xmp), (b"tIME", struct.pack(">HBBBBB", 2026, 3, 15, 9, 30, 0))]) + b"APPENDED")
w("renamed.jpg", png([(b"tEXt", b"Comment\0This is really a PNG file")]))
w("original.pdf", pdf(b"<< /Producer (MetaOrigin Sample) /CreationDate (D:20260101120000Z) /ModDate (D:20260101120000Z) >>"))
w("edited.pdf", pdf(b"<< /Producer (MetaOrigin Sample) /CreationDate (D:20260101120000Z) /ModDate (D:20260101120000Z) >>",
                    b"<< /Producer (Sejda PDF Editor) /CreationDate (D:20260101120000Z) /ModDate (D:20260315093000Z) >>"))
docx(os.path.join(OUT, "original.docx"), core("Sample Author", "Sample Author", "2026-01-01T10:00:00Z", "2026-01-01T10:00:00Z", 1),
     "<w:p><w:r><w:t>Original text</w:t></w:r></w:p>")
docx(os.path.join(OUT, "edited.docx"), core("Sample Author", "Another Editor", "2026-01-01T10:00:00Z", "2026-02-10T16:45:00Z", 7),
     '<w:p><w:r><w:t>Original text</w:t></w:r><w:ins w:id="1" w:author="Another Editor" w:date="2026-02-10T16:45:00Z"><w:r><w:t> added later</w:t></w:r></w:ins></w:p>')
w("camera.jpg", jpeg([(0x10F, "SampleCam"), (0x110, "SC-1"), (0x132, "2026:01:01 10:00:00")]))
w("retouched.jpg", jpeg([(0x10F, "SampleCam"), (0x131, "Adobe Photoshop Lightroom 13"), (0x132, "2026:03:15 09:30:00")]))
w("notes.txt", b"Plain text file with no embedded metadata.\n")
print("samples written to", OUT)
MO_EOF_18
chmod 755 'tests/make_samples.py'
cat > 'tests/run_tests.sh' <<'MO_EOF_19'
#!/usr/bin/env bash
# Offline self-test: builds samples and checks every verdict, the MD5 and the exit codes.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=src/metaorigin.py; S=$(mktemp -d); fail=0
python3 tests/make_samples.py "$S" >/dev/null
chk() { # file expected-verdict
  got=$(python3 $PY --json "$S/$1" | python3 -c "import sys,json;print(json.load(sys.stdin)['verdict'])")
  if [ "$got" = "$2" ]; then printf 'PASS  %-14s %s\n' "$1" "$got"; else printf 'FAIL  %-14s expected %s got %s\n' "$1" "$2" "$got"; fail=1; fi
}
chk original.png "NO EDIT INDICATORS FOUND"; chk edited.png "LIKELY EDITED"
chk original.pdf "NO EDIT INDICATORS FOUND"; chk edited.pdf "LIKELY EDITED"
chk original.docx "NO EDIT INDICATORS FOUND"; chk edited.docx "LIKELY EDITED"
chk camera.jpg "NO EDIT INDICATORS FOUND"; chk retouched.jpg "LIKELY EDITED"
chk renamed.jpg "POSSIBLY EDITED"; chk notes.txt "INCONCLUSIVE"
a=$(python3 $PY --md5 "$S/notes.txt" | cut -d' ' -f1); b=$(md5sum "$S/notes.txt" | cut -d' ' -f1)
[ "$a" = "$b" ] && echo "PASS  md5 matches md5sum" || { echo "FAIL  md5 differs"; fail=1; }
python3 $PY --verify "$b" "$S/notes.txt" >/dev/null && echo "PASS  --verify match exits 0" || { echo "FAIL  --verify match"; fail=1; }
python3 $PY --verify 00000000000000000000000000000000 "$S/notes.txt" >/dev/null; [ $? -eq 1 ] && echo "PASS  --verify mismatch exits 1" || { echo "FAIL  --verify mismatch"; fail=1; }
python3 $PY "$S/missing.bin" >/dev/null 2>&1; [ $? -eq 2 ] && echo "PASS  missing file exits 2" || { echo "FAIL  missing file"; fail=1; }
rm -rf "$S"; [ $fail -eq 0 ] && echo "ALL TESTS PASSED" || { echo "SOME TESTS FAILED"; exit 1; }
MO_EOF_19
chmod 755 'tests/run_tests.sh'
cat > 'docs/index.html' <<'MO_EOF_20'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MetaOrigin</title>
<style>body{font-family:system-ui,sans-serif;background:#0A0E2A;color:#e8e8ff;margin:0;line-height:1.55}
main{max-width:760px;margin:0 auto;padding:32px 20px}h1{color:#00F0FF;margin-bottom:0}h2{color:#A78BFA}
pre{background:#141A4D;border:1px solid #7C3AED;border-radius:8px;padding:12px;overflow:auto}a{color:#39FF14}
.card{background:#141A4D;border:1px solid #7C3AED;border-radius:10px;padding:14px 18px;margin:16px 0}</style></head>
<body><main>
<h1>MetaOrigin</h1><p>Check a file's metadata, get its MD5 sum, and see whether it looks edited or original.</p>
<h2>Install (Kubuntu, Ubuntu, Debian)</h2>
<pre>sudo install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://@@GHUSER@@.github.io/@@GHREPO@@/apt/metaorigin.gpg | sudo tee /etc/apt/keyrings/metaorigin.gpg &gt;/dev/null
printf 'Types: deb\nURIs: https://@@GHUSER@@.github.io/@@GHREPO@@/apt\nSuites: stable\nComponents: main\nSigned-By: /etc/apt/keyrings/metaorigin.gpg\n' | sudo tee /etc/apt/sources.list.d/metaorigin.sources
sudo apt update &amp;&amp; sudo apt install metaorigin</pre>
<h2>Use</h2><pre>metaorigin report.pdf
metaorigin --verify &lt;trusted-md5&gt; report.pdf</pre>
<p>The verdict is a heuristic. Only a match with a trusted hash proves a file is unchanged.</p>
<p><a href="https://github.com/@@GHUSER@@/@@GHREPO@@/releases">Download V1.0 from Releases</a> &middot;
<a href="https://github.com/@@GHUSER@@/@@GHREPO@@">Source code</a></p>
<div class="card"><strong>About</strong><br>@@NAME@@<br>@@DESIGNATION@@, @@COMPANY@@<br>
<a href="mailto:@@EMAIL@@">@@EMAIL@@</a><br>MIT License, V1.0</div>
</main></body></html>
MO_EOF_20
chmod 644 'docs/index.html'
python3 - <<'MO_PY'
import html, json, os, datetime
v = {k: os.environ[k] for k in ("NAME", "EMAIL", "DESIGNATION", "COMPANY", "GHUSER", "GHREPO")}
v["YEAR"] = str(datetime.date.today().year)
for p in ("README.md", "LICENSE", "docs/index.html"):
    t = open(p).read()
    for k, x in v.items():
        t = t.replace("@@%s@@" % k, html.escape(x) if p.endswith(".html") else x)
    open(p, "w").write(t)
a = json.load(open("src/about.json"))
for k in a:
    for key, x in v.items():
        a[k] = a[k].replace("@@%s@@" % key, x)
json.dump(a, open("src/about.json", "w"), indent=2)
MO_PY
bash scripts/bootstrap.sh
echo "Project created in $DEST"
if [ "${1:-}" != "--no-run" ]; then
  bash tests/run_tests.sh
  bash scripts/build_deb.sh
  bash scripts/make_apt_repo.sh
  bash scripts/check_apt_local.sh
  bash scripts/demo.sh
fi
cat <<MSG

DONE. Folder: $DEST
Next, in the browser and terminal:
  bash scripts/git_init.sh https://github.com/$GHUSER/$GHREPO.git
  bash scripts/release_v1.sh
  git push -u origin main --tags
Then on GitHub: Releases > Draft a new release (tag v1.0, attach the files in dist/), and
Settings > Pages > Deploy from a branch > main > /docs.
MSG
