#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import subprocess
import io
from tabulate import tabulate
from ads import environment
import os
import psutil

def get_memory_usage() -> dict:
    """
    Returns memory report as a dictionary

    Parameters
    -----------
    None

    Returns
    -------
    Dict object with following keys - 
        - memory: Total memory used
        - mem_percent_used: Percentage of memory used
        - mem_total: Total memory in the system
        - memory_available: Total available memory for usage.
    """
    memory = psutil.virtual_memory()
    return { 
            "memory": round((memory.total-memory.available)/2**30,2), 
            "mem_percent_used": memory.percent, 
            "mem_total": round(memory.total/2**30 ,2),
            "memory_available": round(memory.available/2**30 ,2)
        }

def check_system() -> list:
    """
    Currently only checks for memory availability. This method can check for all the relevate resources 
    and list all the warning messages.

    """
    memory_report = get_memory_usage()
    messages = []

    if memory_report['memory_available'] < 2:
        message = "Warning: Low memory. Available: {}GB | Usage: {}% | Total: {}GB. {}".format(memory_report['memory_available'], memory_report['mem_percent_used'], memory_report['mem_total'], "" if memory_report['mem_total'] < 3 else "Consider shutting down kernels if you have too many open or del variables not in use")
        messages.append([message])

    return messages
