#!/usr/bin/env python3
""" Vagrant inventory script """
# Adapted from Mark Mandel's implementation
# https://github.com/markmandel/vagrant_ansible_example

import argparse
import io
import json
import os
import sys

import paramiko


def parse_args():
    """command-line options"""
    parser = argparse.ArgumentParser(description="Vagrant inventory script")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true')
    group.add_argument('--host')
    return parser.parse_args()


def list_running_hosts():
    """vagrant.py --list function"""
    cmd = "bash ~/ansibook/chapter_7/vagrant_podman.sh status --machine-readable"
    status = os.popen(cmd).read().rstrip()
    hosts = []
    for line in status.splitlines():
        (_, host, key, value) = line.split(',')[:4]
        if key == 'state' and value == 'running':
            hosts.append(host)
    return hosts


def get_host_details(host):
    """vagrant.py --host <hostname> function"""
    cmd = f'bash ~/ansibook/chapter_7/vagrant_podman.sh ssh-config {host}'
    ssh_config = os.popen(cmd).read()
    config = paramiko.SSHConfig()
    config.parse(io.StringIO(ssh_config))
    host_config = config.lookup(host)
    return {'ansible_host': host_config['hostname'],
            'ansible_port': host_config['port'],
            'ansible_user': host_config['user'],
            'ansible_python_interpreter': '/usr/bin/python3',
            'ansible_private_key_file': host_config['identityfile'][0]}


def main():
    """main"""
    args = parse_args()
    if args.list:
        hosts = list_running_hosts()
        json.dump({'vagrant': hosts}, sys.stdout)
    else:
        details = get_host_details(args.host)
        json.dump(details, sys.stdout)


if __name__ == '__main__':
    main()
