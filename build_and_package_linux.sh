
#!/bin/bash

echo "FajarMandiri Store - Complete Linux Build & Package Script"
echo "=========================================================="

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

print_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is designed to run on Linux"
    exit 1
fi

# Step 1: Build executable
print_step "Step 1: Building Linux executable..."
bash build_linux.sh

if [ $? -ne 0 ]; then
    print_error "Build failed! Stopping process."
    exit 1
fi

echo ""

# Step 2: Create .deb package
print_step "Step 2: Creating .deb package..."
bash package_deb.sh

if [ $? -ne 0 ]; then
    print_error "Packaging failed! Stopping process."
    exit 1
fi

echo ""

# Final summary
print_header "🎉 BUILD AND PACKAGING COMPLETED SUCCESSFULLY! 🎉"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_status "Generated files:"
echo "  📁 dist/fajarmandiri-store (executable)"
echo "  📦 fajarmandiri-store_1.6.0_amd64.deb (installation package)"
echo ""
print_status "Installation details:"
echo "  📍 Application: /opt/fajarmandiri-store/"
echo "  📁 Templates: ~/Documents/FajarMandiriStore/"
echo "  🔗 System command: /usr/bin/fajarmandiri-store"
echo ""
print_status "To install the package:"
echo "  sudo dpkg -i fajarmandiri-store_1.6.0_amd64.deb"
echo ""
print_status "To run the application after installation:"
echo "  fajarmandiri-store"
echo ""
print_status "To uninstall:"
echo "  sudo apt remove fajarmandiri-store"
echo ""
print_status "Features v1.6.0:"
echo "  ✓ Enhanced template serving endpoints"
echo "  ✓ Improved Documents folder integration"
echo "  ✓ Better error handling for missing files"
echo "  ✓ Optimized package structure"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
