#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Requires python 3+")

def hmsString(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

def exitOnError(return_code):
    if return_code != 0:
        sys.exit(1)

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini")
    image_ver = config.get("config", "image")
    architecture = config.get("config", "architecture")
    if config.get("config", "keep-caches").lower() == "false":
        keep_caches = False
    else:
        keep_caches = True
    vm_disk_size = int(config.get("vm", "disk_size"))
    vm_cpus = config.get("vm", "cpus")
    vm_memory = config.get("vm", "memory")
    return image_ver, architecture, keep_caches, vm_disk_size, vm_cpus, vm_memory

def checkLatestImage(URL, image_ver, architecture):
    r = requests.get(URL + "SHA256SUMS")
    hashes = r.text.split('\n')
    latest_version = hashes[0].split()[1].split('-')[2]
    print("[ buildup ] Latest version found: {}".format(latest_version))
    version_name = "{}-{}-{}.iso".format(image_ver, latest_version, architecture)
    for hash in hashes:
        if version_name in hash:
            latest_hash = hash.split()[0]
            break
    latest_iso_url = URL + version_name
    return latest_iso_url, latest_version, version_name, latest_hash

def updatePackerConfig(file_name, latest_iso_url, latest_hash, vm_disk_size, vm_memory, vm_cpus, latest_version):
    with open(file_name) as f:
        packer_config = json.load(f)

    packer_config["builders"][0]["iso_url"] = latest_iso_url
    packer_config["builders"][0]["iso_checksum"] = latest_hash
    packer_config["builders"][0]["disk_size"] = vm_disk_size
    packer_config["builders"][0]["vboxmanage"] = [['modifyvm', '{{.Name}}', '--memory', vm_memory], ['modifyvm', '{{.Name}}', '--cpus', vm_cpus]]
    packer_config["post-processors"][0]["output"] = "build/kali-%s.box" % latest_version

    with open(file_name, "w") as f:
        f.write(json.dumps(packer_config, indent=4, sort_keys=True))

def updateVagrantfile(file_name, latest_version):
    r = re.compile(r"(\s*config.vm.box\s=\s)'.*'")
    with fileinput.FileInput(file_name, inplace=True, backup='.old') as file:
        for line in file:
            print(r.sub(r"\g<1>'kali-%s'" % latest_version, line), end='')

def runPacker(file_name):
    return_code = os.system("packer build %s" % file_name)
    exitOnError(return_code)

def importVagrantBox(latest_version):
    return_code = os.system("vagrant box add kali-{0} build/kali-{0}.box".format(latest_version))
    exitOnError(return_code)

def removeCaches():
    print("[ buildup ] Clearing caches.")
    return_code = os.system("rm -f packer_cache/*")
    exitOnError(return_code)
    return_code = os.system("rm -f build/*")
    exitOnError(return_code)

def vagrantUp():
    return_code = os.system("vagrant up")
    exitOnError(return_code)

if __name__ == "__main__":
    import requests
    import configparser
    import json
    import os
    import time
    import fileinput
    import re

    URL = "https://cdimage.kali.org/current/"
    start = time.time()
    print("[ buildup ] Reading buildup config file.")
    image_ver, architecture, keep_caches, vm_disk_size, vm_cpus, vm_memory = readConfig()

    print("[ buildup ] Getting latest image information.")
    latest_iso_url, latest_version, version_name, latest_hash = checkLatestImage(URL, image_ver, architecture)

    print("[ buildup ] Checking packer config file.")
    file_name = "kali-autobuild.json"
    updatePackerConfig(file_name, latest_iso_url, latest_hash, vm_disk_size, vm_memory, vm_cpus, latest_version)

    print("[ buildup ] Updating Vagrantfile.")
    updateVagrantfile("Vagrantfile", latest_version)

    print("[ buildup ] Starting VM build.")
    runPacker(file_name)

    print("[ buildup ] Importing vagrant box.")
    importVagrantBox(latest_version)

    end = time.time()
    print("[ buildup ] Build complete. Duration: {}".format(hmsString(end - start)))

    if not keep_caches:
        removeCaches()

    print("[ buildup ] Starting vagrant box.")
    vagrantUp()
