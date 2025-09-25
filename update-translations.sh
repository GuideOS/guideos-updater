#!/bin/bash
# Script to extract translatable strings and update .po files

PROJECT_DIR="$(dirname "$0")"
LOCALE_DIR="$PROJECT_DIR/locale"
POT_FILE="$LOCALE_DIR/guideos-updater.pot"

echo "Extracting translatable strings..."

# Extract strings from Python files
find "$PROJECT_DIR" -name "*.py" -not -path "*/.*" -not -path "*/build/*" -not -path "*/debian/*" | \
xgettext --from-code=UTF-8 \
         --language=Python \
         --keyword=_ \
         --keyword=N_ \
         --output="$POT_FILE" \
         --files-from=-

# Add desktop file strings
if [ -f "$PROJECT_DIR/debian/guideos-updater.desktop" ]; then
    echo "Adding desktop file strings..."
    grep -E '^(Name|Comment|GenericName)=' "$PROJECT_DIR/debian/guideos-updater.desktop" | \
    sed 's/^[^=]*=/_("/' | sed 's/$/"/' >> "$POT_FILE.tmp"
    
    # Merge with existing pot file
    msgcat "$POT_FILE" "$POT_FILE.tmp" -o "$POT_FILE"
    rm -f "$POT_FILE.tmp"
fi

echo "Updating German translation..."
if [ -f "$LOCALE_DIR/de/LC_MESSAGES/guideos-updater.po" ]; then
    msgmerge --update "$LOCALE_DIR/de/LC_MESSAGES/guideos-updater.po" "$POT_FILE"
else
    msginit --input="$POT_FILE" \
            --locale=de_DE.UTF-8 \
            --output="$LOCALE_DIR/de/LC_MESSAGES/guideos-updater.po"
fi

echo "Compiling German translation..."
msgfmt "$LOCALE_DIR/de/LC_MESSAGES/guideos-updater.po" \
       -o "$LOCALE_DIR/de/LC_MESSAGES/guideos-updater.mo"

echo "Translation update complete!"