#!/usr/bin/env python3
from setuptools import setup, find_packages
import glob
import os

# Find all locale files
locale_files = []
for mo_path in glob.glob('locale/*/LC_MESSAGES/*.mo'):
    lang = mo_path.split('/')[1]
    locale_files.append((f'share/locale/{lang}/LC_MESSAGES', [mo_path]))

setup(
    name="guideos-updater",
    version="3.1.5",
    description="GuideOS Update Manager for APT and Flatpak",
    long_description="A GUI update manager similar to mintupdate for managing APT and Flatpak updates with PolicyKit integration and German internationalization support",
    author="GuideOS Team",
    author_email="team@guideos.org",
    url="https://github.com/guideos/guideos-updater",
    license="GPL-3.0-or-later",
    packages=find_packages(),
    scripts=['guideos-updater'],
    data_files=[
        ('share/applications', ['debian/guideos-updater.desktop']),
        ('share/polkit-1/actions', ['debian/org.guideos.guideos-updater.policy']),
        ('share/icons/hicolor/scalable/apps', ['guidos-updater.svg']),
        ('share/pixmaps', ['guidos-updater.png']),
    ] + locale_files,
    install_requires=[
        'PyGObject',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Software Distribution",
        "Topic :: Desktop Environment :: Gnome",
    ],
    python_requires='>=3.6',
)