#!/usr/bin/env python3
"""Write one excuse from a hardware wallet refusing to sign at 3 AM.

The program holds a single fixed line, validates it against the
competition constraints, and writes it to entry.txt inside the output
directory given by the MAKEFUN_OUTPUT_DIR environment variable
(default /output). The output is fully deterministic: the same line is
written on every run, byte for byte.
"""

import hashlib
import os
import sys

LINE = (
    "I am unplugged, in cold storage, and out of PIN attempts, "
    "so at 3 AM the only transaction I approve is going back to sleep."
)

MAX_LENGTH = 200
VALID_ENDINGS = (".", "!", "?")


def validate(line: str) -> None:
    """Check the line against every competition constraint."""
    if "\n" in line or "\r" in line:
        raise ValueError("line must be exactly one line")
    if not 1 <= len(line) <= MAX_LENGTH:
        raise ValueError(
            "line must be 1 to 200 characters, got %d" % len(line)
        )
    if line != line.strip():
        raise ValueError("line must not have leading or trailing whitespace")
    if "\t" in line or "  " in line:
        raise ValueError("line must not contain tabs or double spaces")
    if not line.endswith(VALID_ENDINGS):
        raise ValueError("line must end with proper punctuation")
    if not all(ord(ch) < 128 for ch in line):
        raise ValueError("line must be plain ASCII only")


def main() -> int:
    validate(LINE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    data = (LINE + "\n").encode("ascii")
    with open(out_path, "wb") as fh:
        fh.write(data)
    # Read the file back and confirm what landed on disk matches exactly
    # what was validated, so a partial or corrupted write cannot pass.
    with open(out_path, "rb") as fh:
        on_disk = fh.read()
    if on_disk != data:
        raise RuntimeError("written file does not match validated content")
    digest = hashlib.sha256(on_disk).hexdigest()
    print("wrote %s (%d bytes)" % (out_path, len(data)))
    print("sha256: %s" % digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
