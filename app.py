#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from device import Device
from time import sleep
from copy import copy

device = Device()
device.device_name = "Cisco C 3750 G"
device.device_address = "192.168.10.42"
device.snmp_community = "iMAXPublic"
device.snmp_version = "2"
device.connect_device()
curr = [0, 0]
prev = [0, 0]
curr[0] = device.get_input_bandwidth(10105)
curr[1] = device.get_output_bandwidth(10105)
if not prev[0]:
    prev[0] = copy(curr[0])
if not prev[1]:
    prev[1] = copy(curr[1])
sleep(1)
for i in range(50):
    curr[0] = device.get_input_bandwidth(10105)
    curr[1] = device.get_output_bandwidth(10105)
    if curr[0] < prev[0] or curr[1] < prev[1]:
        continue
    else:
        in_speed = int((curr[0] - prev[0]) * 8 / 1024 / 1024)
        out_speed = int((curr[1] - prev[1]) * 8 / 1024 / 1024)
        print("IN: " + str(in_speed) + " Mb/s" + " OUT: " + str(out_speed) + " Mb/s")
        prev[0] = copy(curr[0])
        prev[1] = copy(curr[1])
    sleep(1)