import sys

from utils.pipeline import collect_and_store

if __name__ == "__main__":
    topics = sys.argv[1:] or ["Artificial Intelligence"]
    for t in topics:
        added, warns = collect_and_store(t, language="all")
        print(f"[{t}] added={added} warnings={warns}")
