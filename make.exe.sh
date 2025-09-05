
#!/bin/bash

echo "Building FajarMandiri Store App with custom spec..."

# Check dependencies first
echo "Checking dependencies..."
python check_dependencies.py
if [ $? -ne 0 ]; then
    echo "Dependency check failed. Installing requirements..."
    pip install -r requirements.txt
    
    # Check again
    python check_dependencies.py
    if [ $? -ne 0 ]; then
        echo "Some dependencies are still missing. Please check manually."
        exit 1
    fi
fi

# Clean previous builds
if [ -d "build" ]; then
    rm -rf build
fi
if [ -d "dist" ]; then
    rm -rf dist
fi

echo "Building with PyInstaller..."
pyinstaller app.spec

if [ $? -eq 0 ]; then
    echo "Build completed successfully!"
    echo "Executable location: dist/app.exe"
    
    # Test the executable
    echo "Testing executable..."
    if [ -f "dist/app.exe" ]; then
        echo "✓ Executable created successfully"
        ls -la dist/app.exe
    else
        echo "✗ Executable not found"
    fi
else
    echo "Build failed!"
    exit 1
fi
