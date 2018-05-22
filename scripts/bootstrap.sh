#!/usr/bin/env bash

echo "Initialize MSFDB"
msfdb init
msfdb start

echo "Install zsteg"
gem install zsteg

echo "Install Empire"
git clone https://github.com/PowerShellEmpire/Empire.git
cd Empire/setup
STAGING_KEY=RANDOM ./install.sh
echo "cd /root/Empire && ./empire" >> /usr/bin/empire
chmod +x /usr/bin/empire

echo "Gnome Settings"
gsettings set org.gnome.desktop.screensaver lock-delay 3600
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false

echo "Reboot"
reboot
