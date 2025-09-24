# Python scripts package for Token Creator Widget
# This file makes the directory a Python package

__version__ = "1.0.0"
__author__ = "Token Creator Team"

# Available scripts
AVAILABLE_SCRIPTS = [
    "create_wallet.py",
    "load_wallet.py", 
    "check_balance.py"
]

def get_available_scripts():
    """Return list of available Python scripts"""
    return AVAILABLE_SCRIPTS

def check_script_availability():
    """Check if all required scripts are available"""
    import os
    available = []
    missing = []
    
    for script in AVAILABLE_SCRIPTS:
        if os.path.exists(script):
            available.append(script)
        else:
            missing.append(script)
    
    return {
        "available": available,
        "missing": missing,
        "total": len(AVAILABLE_SCRIPTS),
        "found": len(available)
    }



