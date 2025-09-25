"""
Internationalization support for GuideOS Updater
"""

import gettext
import os
import locale

# Detect locale directory
def get_locale_dir():
    """Get the appropriate locale directory"""
    # First try system-wide installation
    system_locale_dir = '/usr/share/locale'
    if os.path.exists(system_locale_dir):
        return system_locale_dir
    
    # Fallback to local directory for development
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_locale_dir = os.path.join(script_dir, 'locale')
    return local_locale_dir

LOCALE_DIR = get_locale_dir()

# Set up gettext
def setup_i18n():
    """Initialize internationalization"""
    try:
        # Try to get system locale
        current_locale = locale.getdefaultlocale()[0]
        if current_locale is None:
            current_locale = 'en_US'
        
        # Set up gettext
        translation = gettext.translation(
            'guideos-updater', 
            localedir=LOCALE_DIR, 
            languages=[current_locale, 'en'], 
            fallback=True
        )
        translation.install()
        
        # Make _ available globally
        import builtins
        builtins._ = translation.gettext
        
        return translation.gettext
    except Exception as e:
        # Fallback: no translation
        def _(text):
            return text
        import builtins
        builtins._ = _
        return _

# Initialize on import
_ = setup_i18n()