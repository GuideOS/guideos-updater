#!/bin/bash
# Pre-build script to compile translations

set -e

echo "Building translations for GuideOS Updater..."

# Create locale directory if it doesn't exist
mkdir -p locale/de/LC_MESSAGES

# Check if .po file exists
if [ -f "locale/de/LC_MESSAGES/guideos-updater.po" ]; then
    echo "Compiling German translation..."
    msgfmt locale/de/LC_MESSAGES/guideos-updater.po -o locale/de/LC_MESSAGES/guideos-updater.mo
    echo "German translation compiled successfully"
else
    echo "Warning: German .po file not found, creating empty .mo file"
    # Create empty .mo file as fallback
    echo | msgfmt - -o locale/de/LC_MESSAGES/guideos-updater.mo
fi

# Verify .mo files
echo "Checking compiled translations:"
for mo_file in locale/*/LC_MESSAGES/*.mo; do
    if [ -f "$mo_file" ]; then
        lang=$(echo "$mo_file" | cut -d'/' -f2)
        echo "  ✓ $lang: $mo_file"
    fi
done

echo "Translation build complete!"