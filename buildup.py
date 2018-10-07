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

def updatePackerConfig(packer_template, packer_file, latest_iso_url, latest_hash, vm_disk_size, vm_memory, vm_cpus, latest_version):
    with open(packer_template) as f:
        packer_config = json.load(f)

    packer_config["builders"][0]["iso_url"] = latest_iso_url
    packer_config["builders"][0]["iso_checksum"] = latest_hash
    packer_config["builders"][0]["disk_size"] = vm_disk_size
    packer_config["builders"][0]["vboxmanage"] = [['modifyvm', '{{.Name}}', '--memory', vm_memory], ['modifyvm', '{{.Name}}', '--cpus', vm_cpus]]
    packer_config["post-processors"][0]["output"] = "build/kali-{}.box".format(latest_version)

    with open(packer_file, "w") as f:
        f.write(json.dumps(packer_config, indent=4, sort_keys=True))

def updateVagrantfile(vagrant_template, vagrant_file, latest_version, vm_memory, vm_cpus):
    updates = [(re.compile(r"(\s*config.vm.box\s=\s)'.*'"), r"\g<1>'kali-{}'".format(latest_version)),
               (re.compile(r"(\s*config.vm.define\s).*"), r"\g<1>'kali-{}' do |t|".format(latest_version)),
               (re.compile(r"(\s*v.memory\s=\sENV\['VAGRANT_MEMORY'\]\s\|\|\s)\d*"), r"\g<1>{}".format(vm_memory)),
               (re.compile(r"(\s*v.cpus\s=\sENV\['VAGRANT_CPUS'\]\s\|\|\s)\d*"), r"\g<1>{}".format(vm_cpus)),
               (re.compile(r"(\s*v.name\s=\s)'.*'"), r"\g<1>'kali-{}'".format(latest_version))]

    with open(vagrant_template, 'r') as t:
        with open(vagrant_file, 'w') as f:
            for line in t:
                f.write(line)

    for update in updates:
        with fileinput.FileInput(vagrant_file, inplace=True) as f:
            for line in f:
                print(update[0].sub(update[1], line), end='')

def runPacker(file_name):
    return_code = os.system("packer build {}".format(file_name))
    exitOnError(return_code)

def removeOldBoxes():
    return_code = os.system("vagrant box list | grep ^kali- | cut -f 1 -d ' ' | xargs -L 1 vagrant box remove 2>/dev/null")
    if return_code != 0:
        print("No boxes to remove.")

def importVagrantBox(latest_version):
    return_code = os.system("vagrant box add kali-{0} build/kali-{0}.box".format(latest_version))
    exitOnError(return_code)

def removeCaches():
    return_code = os.system("rm -f packer_cache/*")
    exitOnError(return_code)
    return_code = os.system("rm -f build/*")
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
    packer_template = "kali-autobuild.template"
    packer_file = "kali-autobuild.json"
    updatePackerConfig(packer_template, packer_file, latest_iso_url, latest_hash, vm_disk_size, vm_memory, vm_cpus, latest_version)

    print("[ buildup ] Updating Vagrantfile.")
    vagrant_template = "Vagrantfile.template"
    vagrant_file =  "Vagrantfile"
    updateVagrantfile(vagrant_template, vagrant_file, latest_version, vm_memory, vm_cpus)

    print("[ buildup ] Starting VM build.")
    runPacker(packer_file)

    print("[ buildup ] Removing old boxes.")
    removeOldBoxes()

    print("[ buildup ] Importing vagrant box.")
    importVagrantBox(latest_version)

    end = time.time()
    print("[ buildup ] Build complete. Duration: {}".format(hmsString(end - start)))

    if not keep_caches:
        print("[ buildup ] Clearing caches.")
        removeCaches()
