import subprocess
import sys

try:
    import fitz
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF==1.17.3"])

try:
    import PyPDF2
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2==1.26.0"])

try:
    from PyQt5.QtCore import QSortFilterProxyModel, Qt
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5==5.12.2"])