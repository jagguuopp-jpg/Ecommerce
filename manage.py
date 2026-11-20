#!/usr/bin/env python3
"""Root forwarding utility for Pc_store manage.py."""
import os
import sys
import warnings
from pathlib import Path

# Suppress urllib3 and Python 3.9 deprecation warnings in terminal
warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parent
PC_STORE_DIR = ROOT_DIR / "Pc_store"

# Auto-detect .venv site-packages
site_packages = list((ROOT_DIR / ".venv").glob("lib/python*/site-packages"))
if site_packages and str(site_packages[0]) not in sys.path:
    sys.path.insert(0, str(site_packages[0]))

if str(PC_STORE_DIR) not in sys.path:
    sys.path.insert(0, str(PC_STORE_DIR))

# Switch working directory to Pc_store so relative paths match
os.chdir(str(PC_STORE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Pc_store.settings")

if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

