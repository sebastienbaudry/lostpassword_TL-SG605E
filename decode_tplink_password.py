#!/usr/bin/env python3
"""Decode the password field in the tested TP-Link Easy Smart config layout.

Usage:
    python decode_tplink_password.py sauvegarde.cfg
    python decode_tplink_password.py sauvegarde.cfg --offset 0x49

Important:
    The XOR mask and offset below were verified against the supplied TL-SG116E
    backups and one TL-SG605E backup. Other hardware/firmware formats may differ.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_OFFSET = 0x49
DEFAULT_MASK = bytes.fromhex("5c 74 6a 04 7d be b0 b2 fb 6b 06")


def parse_int(value: str) -> int:
    """Allow offsets such as 73 or 0x49."""
    try:
        return int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"invalid offset {value!r}; use decimal (73) or hexadecimal (0x49)"
        ) from exc


def decode_password(data: bytes, offset: int = DEFAULT_OFFSET) -> str:
    """Decode the fixed-length XOR-obfuscated field at *offset*."""
    if offset < 0:
        raise ValueError("offset must be non-negative")

    end = offset + len(DEFAULT_MASK)
    if end > len(data):
        raise ValueError(
            f"file is too short: need {len(DEFAULT_MASK)} bytes at offset "
            f"0x{offset:X}, but file size is {len(data)} bytes"
        )

    stored = data[offset:end]
    decoded = bytes(value ^ mask for value, mask in zip(stored, DEFAULT_MASK))

    # The tested format pads passwords on the right with NUL bytes.
    decoded = decoded.rstrip(b"\x00")

    try:
        password = decoded.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "decoded bytes are not ASCII; this may be the wrong offset, an "
            "unsupported backup format, or a different encoding"
        ) from exc

    if not password or any(ord(ch) < 0x20 or ord(ch) > 0x7E for ch in password):
        raise ValueError(
            "decoded value is empty or contains non-printable characters; "
            "the file may not use the tested format"
        )

    return password


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decode the password field in a tested TP-Link Easy Smart backup."
    )
    parser.add_argument("file", type=Path, help="path to the binary .cfg backup")
    parser.add_argument(
        "--offset",
        type=parse_int,
        default=DEFAULT_OFFSET,
        help="byte offset of the 11-byte password field (default: 0x49)",
    )
    args = parser.parse_args()

    try:
        data = args.file.read_bytes()
        password = decode_password(data, args.offset)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # Print the recovered credential only to stdout; avoid writing it to disk.
    print(password)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
