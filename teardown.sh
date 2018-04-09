#!/bin/bash

vagrant destroy -f

vagrant box remove kali-rolling

if [ -f build/kali-rolling.box ]; then
	rm build/kali-rolling.box
fi

