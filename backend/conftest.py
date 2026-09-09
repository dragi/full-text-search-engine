import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# The tests exercise the API against small, hand-built corpora; never index the
# bundled Wikipedia sample on app startup.
os.environ.setdefault("SKIP_CORPUS", "1")
