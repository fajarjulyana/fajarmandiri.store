
import subprocess
import os
import sys
import platform
import threading
import time
import signal
import json
import shutil
from pathlib import Path

class CloudflareTunnel:
    def __init__(self):
        self.process = None
        self.config_path = None
        self.credentials_path = None
        self.tunnel_name = "kasir"
        self.setup_paths()
    
    def setup_paths(self):
        """Setup path konfigurasi berdasarkan OS"""
        system = platform.system()
        
        if system == "Windows":
            # Windows paths
            cloudflared_dir = Path.home() / ".cloudflared"
            self.config_path = cloudflared_dir / "config.yml"
            self.credentials_path = cloudflared_dir / "7dfdc496-a179-4074-8baa-9d6a9c5a59ec.json"
            self.cloudflared_exe = "cloudflared.exe"
        else:
            # Linux paths
            cloudflared_dir = Path.home() / ".cloudflared"
            self.config_path = cloudflared_dir / "config.yml"
            self.credentials_path = cloudflared_dir / "7dfdc496-a179-4074-8baa-9d6a9c5a59ec.json"
            self.cloudflared_exe = "cloudflared"
        
        # Buat direktori jika belum ada
        cloudflared_dir.mkdir(exist_ok=True)
    
    def copy_config_files(self):
        """Copy file konfigurasi dari attached_assets"""
        try:
            # Copy config.yml
            config_source = Path("attached_assets/config_1756723528559.yml")
            if config_source.exists():
                # Update config untuk path yang benar
                with open(config_source, 'r') as f:
                    config_content = f.read()
                
                # Replace Windows path dengan path yang sesuai OS
                config_content = config_content.replace(
                    r"C:\Users\FJ-PC\.cloudflared\7dfdc496-a179-4074-8baa-9d6a9c5a59ec.json",
                    str(self.credentials_path)
                )
                
                with open(self.config_path, 'w') as f:
                    f.write(config_content)
                print(f" Config copied to {self.config_path}")
            
            # Copy credentials file
            creds_source = Path("attached_assets/7dfdc496-a179-4074-8baa-9d6a9c5a59ec_1756723528560.json")
            if creds_source.exists():
                shutil.copy2(creds_source, self.credentials_path)
                print(f" Credentials copied to {self.credentials_path}")
            
            return True
        except Exception as e:
            print(f"Error copying config files: {e}")
            return False
    
    def check_cloudflared_installed(self):
        """Cek apakah cloudflared sudah terinstall"""
        try:
            subprocess.run([self.cloudflared_exe, "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_cloudflared(self):
        """Install cloudflared berdasarkan OS"""
        system = platform.system()
        
        try:
            if system == "Windows":
                print("Please download cloudflared.exe from:")
                print("https://github.com/cloudflare/cloudflared/releases/latest")
                print("Place it in your PATH or in the application directory")
                return False
            
            elif system == "Linux":
                # Install untuk Linux
                print("Installing cloudflared for Linux...")
                subprocess.run([
                    "curl", "-L", "--output", "cloudflared.deb",
                    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
                ], check=True)
                
                subprocess.run(["sudo", "dpkg", "-i", "cloudflared.deb"], check=True)
                os.remove("cloudflared.deb")
                return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error installing cloudflared: {e}")
            return False
    
    def start_tunnel(self):
        """Start Cloudflare tunnel dalam thread terpisah"""
        if not self.check_cloudflared_installed():
            print("Cloudflared not found, attempting to install...")
            if not self.install_cloudflared():
                print("Failed to install cloudflared. Please install manually.")
                return False
        
        # Copy config files
        if not self.copy_config_files():
            print("Failed to setup config files")
            return False
        
        def run_tunnel():
            try:
                print(f"Starting Cloudflare tunnel: {self.tunnel_name}")
                
                # Command untuk run tunnel
                cmd = [self.cloudflared_exe, "tunnel", "--config", str(self.config_path), "run", self.tunnel_name]
                
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Monitor output
                for line in iter(self.process.stdout.readline, ''):
                    if line.strip():
                        print(f"[Cloudflare] {line.strip()}")
                        if "started tunnel" in line.lower() or "registered tunnel connection" in line.lower():
                            print(" Tunnel connected successfully!")
                            print(" Domain accessible: https://fajarmandiri.store")
                            print(" Kasir accessible: https://kasir.fajarmandiri.store")
                
            except Exception as e:
                print(f"Error running tunnel: {e}")
        
        # Start tunnel dalam thread terpisah
        tunnel_thread = threading.Thread(target=run_tunnel, daemon=True)
        tunnel_thread.start()
        
        # Tunggu sebentar untuk memastikan tunnel start
        time.sleep(3)
        
        return True
    
    def stop_tunnel(self):
        """Stop tunnel process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print(" Tunnel stopped")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print(" Tunnel force stopped")
            except Exception as e:
                print(f"Error stopping tunnel: {e}")
    
    def is_running(self):
        """Cek apakah tunnel sedang berjalan"""
        return self.process and self.process.poll() is None

# Global instance
tunnel_manager = CloudflareTunnel()

def start_tunnel_on_startup():
    """Function untuk start tunnel saat startup"""
    return tunnel_manager.start_tunnel()

def stop_tunnel_on_shutdown():
    """Function untuk stop tunnel saat shutdown"""
    tunnel_manager.stop_tunnel()
