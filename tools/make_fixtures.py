"""Write a NEW synthetic fixture directory; no real research export is used."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quoteledger.core import canonical
from tools.corpus import authored, generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    for name, rows in (("authored", authored()), ("generated", generated())):
        (args.output / (name + ".json")).write_bytes(canonical({
            "schema": "quoteledger.synthetic-corpus.v1",
            "family": name, "cases": rows,
            "note": "Fictional implementation checks, not real studies or independent observations.",
        }))
    print("Synthetic fixtures created.")


if __name__ == "__main__":
    main()