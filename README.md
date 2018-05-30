# kali-autobuild

This repo is my starting point for quickly getting up and running with latest Kali.

Simply locates latest kali build based on your settings then downloads iso, installs into a VM with a preseed, and finally packs into a vagrant box for your use.

# Dependancies
Tested/Built with:
+ Vagrant 2.0.3
+ Packer 1.0.2
+ VirtualBox 5.2.8
+ Active internet connection

Note: will probably work with lower versions but I have not tested.

# Getting Started
1. `git clone github.com/nodocify/kali-autobuild`
2. Edit `config.ini` for your needs. See below for options.
3. (optional) Modify `scripts/bootstrap.sh`. For example, to install all updates. (Only the kernel is updated in the build process).
4. `./buildup.py`

Note: This will take some time to build. Approx 30 minutes for my system. Might be a good time to get coffee.
You will have a functional VM with your customizations once it is complete.

## config.ini options
All sections and options are currently required.

### [config] section
#### architecture
Can be one of the following:
+ amd64
+ i386
+ armh

#### image
Can be one of the following:
+ kali-linux
+ kali-linux-e17
+ kali-linux-light
+ kali-linux-kde
+ kali-linux-lxde
+ kali-linux-mate
+ kali-linux-xfce

#### keep-caches
Can be either `True` or `False`.

During build process ISOs are downloaded and `.box` is created. If set to `False` once the build completes all downloaded/created files are removed leaving only box that is imported into Vagrant. A consideration to make if you don't have much hard drive space as `packer_cache` plus `build` directories holds about 8Gb worth of space when done.

### [vm] section
#### disk-size
Size in MB of the hard drive that is created for the VM.

#### cpus
Number of CPUs to allocate to the VM.

#### memory
Amount of RAM in MB to allocate to the VM.

# To Do
+ Proper error checking of config file. For example, i386 architecture is only available on the base and light images. Verify that required sections are present.
+ Convert vagrant provisioner from shell to puppet apply.
