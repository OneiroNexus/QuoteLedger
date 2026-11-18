"""Build a deterministic standard-library zipapp without network access."""
from pathlib import Path
import argparse
import io
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def archive():
    entries = {"__main__.py": b"from quoteledger.cli import main\nraise SystemExit(main())\n"}
    for path in sorted((ROOT / "quoteledger").glob("*.py")):
        entries["quoteledger/" + path.name] = path.read_bytes()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as out:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            out.writestr(info, data)
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with args.output.open("xb") as out:
        out.write(archive())
    print("QuoteLedger zipapp created.")


if __name__ == "__main__":
    main()