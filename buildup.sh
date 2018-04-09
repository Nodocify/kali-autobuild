#!/bin/bash

packer build kali-rolling.json
vagrant box add kali-rolling build/kali-rolling.box
vagrant up
