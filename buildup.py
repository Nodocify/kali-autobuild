#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Requires python 3+")

import requests
import configparser
import json
import os
import time

def hmsString(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

def exitOnError(return_code):
    if return_code != 0:
        sys.exit(1)

start_time = time.time()
print("[ buildup ] Reading config file.")
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

CURRENT_URL = "https://cdimage.kali.org/current/"

print("[ buildup ] Getting latest image information.")
r = requests.get(CURRENT_URL + "SHA256SUMS")
hashes = r.text.split('\n')
latest_version = hashes[0].split()[1].split('-')[2]
print("[ buildup ] Latest version found: {}".format(latest_version))
version_name = "{}-{}-{}.iso".format(image_ver, latest_version, architecture)
for hash in hashes:
    if version_name in hash:
        latest_hash = hash.split()[0]
        break
latest_iso_url = CURRENT_URL + version_name

print("[ buildup ] Checking config file.")
file_name = "kali-rolling.json"
with open(file_name) as f:
    packer_config = json.load(f)

packer_config["builders"][0]["iso_url"] = latest_iso_url
packer_config["builders"][0]["iso_checksum"] = latest_hash
packer_config["builders"][0]["disk_size"] = vm_disk_size
packer_config["post-processors"][0]["output"] = "build/kali-%s.box" % latest_version
packer_config["builders"][0]["vboxmanage"] = [['modifyvm', '{{.Name}}', '--memory', vm_memory], ['modifyvm', '{{.Name}}', '--cpus', vm_cpus]]

with open(file_name, "w") as f:
    f.write(json.dumps(packer_config, indent=4, sort_keys=True))

print("[ buildup ] Starting VM build.")
return_code = os.system("packer build %s" % file_name)
exitOnError(return_code)

print("[ buildup ] Importing vagrant box.")
return_code = os.system("vagrant box add kali-autobuild build/kali-%s.box" % latest_version)
exitOnError(return_code)


end_time = time.time()
print("[ buildup ] Build complete. Duration: {}".format(hmsString(end - start)))

if not keep_caches:
    print("[ buildup ] Clearing caches.")
    return_code = os.system("rm -f packer_cache/*")
    exitOnError(return_code)
    return_code = os.system("rm -f build/*")
    exitOnError(return_code)

print("[ buildup ] Starting vagrant box.")
return_code = os.system("vagrant up")
exitOnError(return_code)
