
#!/bin/bash

echo "Installing Cloudflared for Linux..."

# Set colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if already installed
if command -v cloudflared &> /dev/null; then
    print_status "Cloudflared already installed"
    cloudflared --version
    exit 0
fi

# Download and install
print_status "Downloading cloudflared..."
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

if [ $? -eq 0 ]; then
    print_status "Installing cloudflared..."
    sudo dpkg -i cloudflared.deb
    
    if [ $? -eq 0 ]; then
        print_status " Cloudflared installed successfully!"
        cloudflared --version
        rm cloudflared.deb
    else
        print_error " Failed to install cloudflared"
        exit 1
    fi
else
    print_error " Failed to download cloudflared"
    exit 1
fi
