"""Root conftest: add src/ to sys.path so bare 'threat_modeler' imports resolve."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
