"""
Entry point called by GitHub Actions.
"""
import sys
sys.path.insert(0, "src")

from config import Config
from main   import run

cfg = Config()
run(cfg)
