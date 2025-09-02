
#!/bin/bash

echo "Creating .deb package for FajarMandiri Store..."

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if executable exists
if [ ! -f "dist/fajarmandiri-store" ]; then
    print_error "Executable not found. Please run build_linux.sh first."
    exit 1
fi

# Package information
PACKAGE_NAME="fajarmandiri-store"
VERSION="1.6.0"
ARCHITECTURE="amd64"
MAINTAINER="Fajar Mandiri Store <info@fajarmandiri.store>"
DESCRIPTION="Fajar Mandiri Store - Server aplikasi fotokopi, printing, dan undangan digital"

# Create package directory structure
PACKAGE_DIR="deb_package"
DEB_DIR="${PACKAGE_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}"

print_status "Creating package directory structure..."
rm -rf $PACKAGE_DIR
mkdir -p $DEB_DIR/DEBIAN
mkdir -p $DEB_DIR/opt/fajarmandiri-store
mkdir -p $DEB_DIR/usr/share/applications
mkdir -p $DEB_DIR/usr/share/pixmaps
mkdir -p $DEB_DIR/usr/bin

# Copy executable and assets
print_status "Copying application files..."
cp dist/fajarmandiri-store $DEB_DIR/opt/fajarmandiri-store/
cp -r dist/_internal/* $DEB_DIR/opt/fajarmandiri-store/ 2>/dev/null || true
cp fajarmandiri.db $DEB_DIR/opt/fajarmandiri-store/
cp -r templates $DEB_DIR/opt/fajarmandiri-store/
cp -r static $DEB_DIR/opt/fajarmandiri-store/
cp copy_templates_to_documents.py $DEB_DIR/opt/fajarmandiri-store/
cp cloudflare_tunnel.py $DEB_DIR/opt/fajarmandiri-store/

# Create icon if exists
if [ -f "icon.ico" ]; then
    # Convert .ico to .png if ImageMagick is available
    if command -v convert &> /dev/null; then
        convert icon.ico $DEB_DIR/usr/share/pixmaps/fajarmandiri-store.png 2>/dev/null || cp icon.ico $DEB_DIR/usr/share/pixmaps/fajarmandiri-store.ico
    else
        cp icon.ico $DEB_DIR/usr/share/pixmaps/fajarmandiri-store.ico
    fi
fi

# Create launcher script
print_status "Creating launcher script..."
cat > $DEB_DIR/usr/bin/fajarmandiri-store << 'EOF'
#!/bin/bash
cd /opt/fajarmandiri-store
exec ./fajarmandiri-store "$@"
EOF
chmod +x $DEB_DIR/usr/bin/fajarmandiri-store

# Create desktop entry
print_status "Creating desktop entry..."
cat > $DEB_DIR/usr/share/applications/fajarmandiri-store.desktop << EOF
[Desktop Entry]
Name=Fajar Mandiri Store
Comment=Server aplikasi fotokopi, printing, dan undangan digital
Exec=/usr/bin/fajarmandiri-store
Icon=fajarmandiri-store
Terminal=false
Type=Application
Categories=Office;Network;
StartupNotify=true
EOF

# Create control file
print_status "Creating DEBIAN control file..."
cat > $DEB_DIR/DEBIAN/control << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCHITECTURE
Depends: libc6, python3, python3-tk
Maintainer: $MAINTAINER
Description: $DESCRIPTION
 Fajar Mandiri Store adalah aplikasi server untuk layanan fotokopi,
 printing, dan pembuatan undangan digital. Aplikasi ini menyediakan
 antarmuka web untuk mengelola pesanan dan template.
 .
 Fitur utama:
  - Manajemen pesanan fotokopi dan printing
  - Generator undangan pernikahan digital
  - Template undangan yang dapat dikustomisasi
  - Interface web yang responsif
  - Sistem admin terintegrasi
EOF

# Create postinst script
print_status "Creating post-installation script..."
cat > $DEB_DIR/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

# Set permissions
chmod +x /opt/fajarmandiri-store/fajarmandiri-store
chmod +x /usr/bin/fajarmandiri-store

# Create symlink if it doesn't exist
if [ ! -L /usr/local/bin/fajarmandiri-store ]; then
    ln -sf /usr/bin/fajarmandiri-store /usr/local/bin/fajarmandiri-store
fi

# Setup templates in user Documents for the current user
USER_HOME=$(eval echo ~$SUDO_USER)
if [ ! -z "$USER_HOME" ] && [ "$USER_HOME" != "/root" ]; then
    echo "Setting up templates in Documents for user: $SUDO_USER"
    sudo -u $SUDO_USER python3 /opt/fajarmandiri-store/copy_templates_to_documents.py 2>/dev/null || true
else
    echo "Note: Run 'python3 /opt/fajarmandiri-store/copy_templates_to_documents.py' to setup templates in your Documents folder"
fi

echo ""
echo "==================================="
echo "Fajar Mandiri Store v1.6.0 installed successfully!"
echo "==================================="
echo ""
echo "Application installed to: /opt/fajarmandiri-store/"
echo "Templates copied to: ~/Documents/FajarMandiriStore/"
echo ""
echo "To start the application:"
echo "  fajarmandiri-store"
echo ""
echo "Or find it in your applications menu."
echo ""

exit 0
EOF
chmod +x $DEB_DIR/DEBIAN/postinst

# Create prerm script
print_status "Creating pre-removal script..."
cat > $DEB_DIR/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e

# Remove symlink
if [ -L /usr/local/bin/fajarmandiri-store ]; then
    rm -f /usr/local/bin/fajarmandiri-store
fi

exit 0
EOF
chmod +x $DEB_DIR/DEBIAN/prerm

# Set permissions
print_status "Setting permissions..."
find $DEB_DIR -type f -exec chmod 644 {} \;
find $DEB_DIR -type d -exec chmod 755 {} \;
chmod +x $DEB_DIR/opt/fajarmandiri-store/fajarmandiri-store
chmod +x $DEB_DIR/usr/bin/fajarmandiri-store
chmod +x $DEB_DIR/DEBIAN/postinst
chmod +x $DEB_DIR/DEBIAN/prerm

# Build the package
print_status "Building .deb package..."
dpkg-deb --build $DEB_DIR

if [ $? -eq 0 ]; then
    print_status "✓ Package created successfully!"
    
    # Move to root directory
    mv ${DEB_DIR}.deb ./
    
    print_header "Package Information:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Package: ${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb"
    echo "Size: $(du -h ${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb | cut -f1)"
    echo "Location: $(pwd)/${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    print_status "Installation command:"
    echo "sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb"
    
    print_status "Uninstallation command:"
    echo "sudo apt remove $PACKAGE_NAME"
    
    # Clean up
    rm -rf $PACKAGE_DIR
    
else
    print_error "✗ Package creation failed!"
    exit 1
fi

print_status ".deb package creation completed successfully!"
