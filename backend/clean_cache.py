"""
Clean all __pycache__ directories and .pyc files
"""
import os
import shutil

def clean_cache():
    """Remove all __pycache__ directories and .pyc files"""
    removed_dirs = 0
    removed_files = 0
    
    print("=" * 80)
    print("🧹 Cleaning Python cache files...")
    print("=" * 80)
    print()
    
    # Walk through all directories
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_path)
                print(f"✅ Removed: {cache_path}")
                removed_dirs += 1
            except Exception as e:
                print(f"❌ Failed to remove {cache_path}: {e}")
        
        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"✅ Removed: {file_path}")
                    removed_files += 1
                except Exception as e:
                    print(f"❌ Failed to remove {file_path}: {e}")
    
    print()
    print("=" * 80)
    print(f"✅ Cleaning complete!")
    print(f"   - Removed {removed_dirs} __pycache__ directories")
    print(f"   - Removed {removed_files} .pyc files")
    print("=" * 80)
    print()
    print("🚀 Now restart Django server:")
    print("   python manage.py runserver 8000")
    print()

if __name__ == '__main__':
    clean_cache()
