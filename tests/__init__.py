# Enable vscode django unittesting

from django import setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "site_proj.settings")
setup()