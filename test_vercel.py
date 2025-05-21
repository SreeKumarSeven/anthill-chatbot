#!/usr/bin/env python
"""
Test script to verify the Vercel deployment code can be imported without errors.
This helps catch import-time errors before deploying.
"""
import os
import sys
import importlib
import importlib.util

def test_import_module(module_path, module_name=None):
    """Try to import a module and return True if successful."""
    if module_name is None:
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        
    print(f"Testing import of {module_name} from {module_path}...")
    
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ Successfully imported {module_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to import {module_name}:")
        print(f"   Error: {str(e)}")
        return False

def main():
    """Main test function to check all Vercel deployment files."""
    print("Testing Vercel deployment files...\n")
    
    # Add the current directory to sys.path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # List of modules to test
    modules = [
        ("api/index.py", "index"),
        ("api/simple_db.py", "simple_db"),
        ("api/service_account_handler.py", "service_account_handler")
    ]
    
    # Test each module
    all_success = True
    for module_path, module_name in modules:
        success = test_import_module(module_path, module_name)
        all_success = all_success and success
        print("")  # Add a blank line between tests
    
    # Print summary
    if all_success:
        print("All modules imported successfully! ✨")
        return 0
    else:
        print("One or more modules failed to import. Please fix the errors before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 