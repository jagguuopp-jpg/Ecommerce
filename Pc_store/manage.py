#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
import warnings
from pathlib import Path

# Suppress urllib3 and Python 3.9 deprecation warnings in terminal
warnings.filterwarnings("ignore")

# Auto-detect workspace virtualenv so running system 'python3 manage.py' works directly without manual activation
BASE_DIR = Path(__file__).resolve().parent

for venv_candidate in [BASE_DIR / '.venv', BASE_DIR.parent / '.venv']:
    site_packages = list(venv_candidate.glob('lib/python*/site-packages'))
    if site_packages and str(site_packages[0]) not in sys.path:
        sys.path.insert(0, str(site_packages[0]))
        break


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Pc_store.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
