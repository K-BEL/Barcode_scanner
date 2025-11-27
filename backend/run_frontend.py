"""Script to run the Streamlit frontend."""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    frontend_path = Path(__file__).parent / "app" / "frontend" / "main.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(frontend_path)])

