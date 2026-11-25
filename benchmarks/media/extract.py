#!/usr/bin/env python3
"""Verify and extract the deduplicated benchmark media archive.

Usage:
  python3 benchmarks/media/extract.py --check   # verify archive parts/hash
  python3 benchmarks/media/extract.py           # extract, then verify every file

The gzip tar stores 112 logical paths but only 63 unique payloads using
hardlinks. It is split into 80 MiB parts to stay below GitHub's file-size
limit; the parts are streamed as one archive during extraction.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
MANIFEST = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
PARTS = [REPO_ROOT / p["path"] for p in MANIFEST["archive"]["parts"]]


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def archive_hash():
    h = hashlib.sha256()
    for path in PARTS:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
    return h.hexdigest()


@contextmanager
def archive_stream():
    proc = subprocess.Popen(["cat", *map(str, PARTS)], stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|gz") as tf:
            yield tf
    finally:
        if proc.stdout:
            proc.stdout.close()
        code = proc.wait()
        if code != 0:
            raise SystemExit(f"archive stream failed with exit code {code}")


def verify_archive():
    for meta, path in zip(MANIFEST["archive"]["parts"], PARTS):
        if not path.is_file():
            raise SystemExit(f"missing archive part: {path}")
        if path.stat().st_size != meta["bytes"] or sha256(path) != meta["sha256"]:
            raise SystemExit(f"archive part hash mismatch: {path}")
    if archive_hash() != MANIFEST["archive"]["sha256"]:
        raise SystemExit("combined archive SHA-256 mismatch")
    with archive_stream() as tf:
        count = sum(1 for m in tf if m.isfile() or m.islnk())
    if count != MANIFEST["archive"]["logicalFileCount"]:
        raise SystemExit(f"archive member count mismatch: {count}")
    print(f"archive OK: {len(PARTS)} parts, {count} logical files, "
          f"{MANIFEST['archive']['uniqueFileCount']} unique payloads")


def verify_files():
    errors = []
    for entry in MANIFEST["files"]:
        path = REPO_ROOT / entry["path"]
        if not path.is_file():
            errors.append(f"missing: {entry['path']}")
            continue
        if path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            errors.append(f"hash mismatch: {entry['path']}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"files OK: {len(MANIFEST['files'])} extracted paths verified")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify archive without extracting")
    args = parser.parse_args()
    verify_archive()
    if not args.check:
        with archive_stream() as tf:
            tf.extractall(ROOT, filter="data")
        verify_files()
        print(f"extracted to {ROOT}")


if __name__ == "__main__":
    main()
