# lostpassword_TL-SG605E
retrieve your TL-SG605E or TL-SG116E switch password from your backup cfg file

This repository contains `decode\_tplink\_password.py`, a small Python script that reads a binary `.cfg` backup and decodes the 11-byte field examined in the test backups.

> \*\*Important limitation:\*\* The behavior was checked against the supplied test files for the TL-SG116E and TL-SG605E models. It is not guaranteed to work with every TP-Link hardware revision, firmware version, or backup format.

## Requirements

* Python 3; no third-party libraries are required.
* A binary `.cfg` backup that you are authorized to access.

## Usage

Place the script and the backup file in the same directory, then run:

```bash
python decode\_tplink\_password.py backup.cfg
```

On some systems, use `python3` instead of `python`:

```bash
python3 decode\_tplink\_password.py backup.cfg
```

The script prints the result in the terminal. It does not write the password to a file.

### Changing the offset

By default, the script looks for the field at offset `0x49`. If you have established that the field starts elsewhere in a compatible file, specify the offset in decimal or hexadecimal:

```bash
python decode\_tplink\_password.py backup.cfg --offset 0x49
```

To display all available options, run:

```bash
python decode\_tplink\_password.py --help
```

## Default Parameters

|Parameter|Value|
|-|-|
|Field offset|`0x49` (73 in decimal)|
|Field length|11 bytes|
|XOR mask|`5c746a047dbeb0b2fb6b06`|
|Expected encoding|Printable ASCII|
|Observed padding|Null bytes (`00`) on the right|

The script applies a byte-by-byte XOR between the stored data and the mask, then removes trailing null bytes.

## Error Messages

The script stops with an error message if:

* the file cannot be read;
* the file is too short to contain the field at the specified offset;
* the decoded result is not printable ASCII, which may indicate an incorrect offset, a different format, or an unsupported encoding.

A plausible-looking result does not, by itself, guarantee that the field was interpreted correctly. Check the model and firmware version before using the script with another backup.

## Security and Privacy

* Backup files may contain sensitive information, including network settings, configuration data, and credentials.
* Work on a copy of the file and keep backups in a secure location.
* Avoid copying terminal output into logs or sharing it with others.
* Use this script only with devices and backups you are authorized to access.

