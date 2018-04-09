# kali-autobuild

This repo is my starting point for quickly getting up and running with latest Kali.

Uses packer to securely download the Kali ISO and preseed install into a VM. Then pack that VM into a vagrant box.

# Dependancies
Tested/Built with:
+ Vagrant 2.0.3
+ Packer 1.0.2
+ VirtualBox 5.2.8

Note: will probably work with lower versions but I have not tested.

# Get started
1. `git clone github.com/nodocify/kali-autobuild`
2. (optional) Modify `scripts/bootstrap.sh`. For example, to install all updates. (Only the kernel is updated in the build process).
3. `./buildup.sh`
WARNING: This will take some time to build. Approx 30 minutes for my system. Might be a good time to get coffee.
You will have a functional VM with your customizations once it is complete.
