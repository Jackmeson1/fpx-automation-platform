import os
import sys
from pathlib import Path

pysys_root: str = Path(os.path.dirname(os.path.abspath(__file__))).parent
sys.path.append(pysys_root)

