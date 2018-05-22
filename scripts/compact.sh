#!/usr/bin/env bash

apt autoremove -y
apt clean

if [ -f /var/lib/dpkg/lock ]; then
	rm /var/lib/dpkg/lock
fi

if [ -f /var/cache/apt/archives/lock ]; then
	rm /var/cache/apt/archives/lock
fi

dd if=/dev/zero of=/junk bs=1M
rm -f /junk

sync
