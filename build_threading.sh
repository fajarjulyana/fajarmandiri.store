
#!/bin/bash

echo "Building FajarMandiri Store App (Threading Mode)..."

# Check dependencies
echo "Checking dependencies..."
python check_dependencies.py

# Clean previous builds
if [ -d "build" ]; then
    echo "Cleaning build directory..."
    rm -rf build
fi
if [ -d "dist" ]; then
    echo "Cleaning dist directory..."
    rm -rf dist
fi

# Build using threading-specific spec
echo "Building with PyInstaller (Threading mode)..."
pyinstaller app_threading.spec

if [ $? -eq 0 ]; then
    echo "Build completed successfully!"
    echo "Executable: dist/FajarMandiriStore.exe"
    
    if [ -f "dist/FajarMandiriStore.exe" ]; then
        echo "✓ Executable created successfully"
        ls -la dist/FajarMandiriStore.exe
    else
        echo "✗ Executable not found"
        exit 1
    fi
else
    echo "Build failed!"
    exit 1
fi
