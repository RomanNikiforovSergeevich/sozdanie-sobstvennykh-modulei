#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: yc_instance
short_description: Manage Yandex Cloud VM instances
version_added: "1.0.0"
description:
    - Creates or deletes VM instances in Yandex Cloud using yc CLI.
    - Requires the yc command-line tool to be installed and authenticated.
options:
    name:
        description: Instance name.
        required: true
        type: str
    folder_id:
        description: Yandex Cloud folder ID.
        required: true
        type: str
    zone:
        description: Availability zone.
        required: false
        type: str
        default: ru-central1-a
    cores:
        description: Number of CPU cores.
        required: false
        type: int
        default: 2
    memory:
        description: RAM in GB.
        required: false
        type: int
        default: 2
    core_fraction:
        description: CPU core fraction.
        required: false
        type: int
        default: 20
    image_family:
        description: OS image family.
        required: false
        type: str
        default: ubuntu-2204-lts
    disk_size:
        description: Boot disk size in GB.
        required: false
        type: int
        default: 10
    subnet_id:
        description: Subnet ID.
        required: true
        type: str
    ssh_public_key:
        description: Public SSH key to add to metadata.
        required: false
        type: str
        default: ""
    preemptible:
        description: Make instance preemptible.
        required: false
        type: bool
        default: true
    state:
        description: Desired state.
        required: false
        type: str
        default: present
        choices: [present, absent]
author:
    - Roman Nikiforov (@RomanNikiforovSergeevich)
'''

EXAMPLES = r'''
- name: Create VM
  my_own_namespace.yandex_cloud_elk.yc_instance:
    name: my-vm
    folder_id: b1g...
    subnet_id: e9b...
    cores: 2
    memory: 2
    image_family: ubuntu-2204-lts
    ssh_public_key: "ssh-ed25519 AAAA..."

- name: Delete VM
  my_own_namespace.yandex_cloud_elk.yc_instance:
    name: my-vm
    folder_id: b1g...
    subnet_id: e9b...
    state: absent
'''

RETURN = r'''
instance_id:
    description: ID of the created/existing instance.
    type: str
    returned: always
    sample: fhm...
external_ip:
    description: External IP address of the instance.
    type: str
    returned: when state=present
    sample: 84.201.xxx.xxx
'''

import json
import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_yc(args, module):
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        module.fail_json(msg=f"yc command failed: {e.stderr}")


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        folder_id=dict(type='str', required=True),
        zone=dict(type='str', required=False, default='ru-central1-a'),
        cores=dict(type='int', required=False, default=2),
        memory=dict(type='int', required=False, default=2),
        core_fraction=dict(type='int', required=False, default=20),
        image_family=dict(type='str', required=False, default='ubuntu-2204-lts'),
        disk_size=dict(type='int', required=False, default=10),
        subnet_id=dict(type='str', required=True),
        ssh_public_key=dict(type='str', required=False, default=''),
        preemptible=dict(type='bool', required=False, default=True),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
    )

    result = dict(changed=False, instance_id='', external_ip='')

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(**result)

    name = module.params['name']
    folder_id = module.params['folder_id']
    state = module.params['state']

    list_out = run_yc(
        ['yc', 'compute', 'instance', 'list', '--folder-id', folder_id, '--format', 'json'],
        module
    )
    instances = json.loads(list_out) if list_out.strip() else []
    existing = [i for i in instances if i.get('name') == name]

    if state == 'present':
        if existing:
            inst = existing[0]
            result['instance_id'] = inst['id']
            nics = inst.get('network_interfaces', [])
            if nics and nics[0].get('primary_v4_address', {}).get('one_to_one_nat', {}).get('address'):
                result['external_ip'] = nics[0]['primary_v4_address']['one_to_one_nat']['address']
            module.exit_json(**result)

        cmd = [
            'yc', 'compute', 'instance', 'create',
            '--name', name,
            '--folder-id', folder_id,
            '--zone', module.params['zone'],
            '--cores', str(module.params['cores']),
            '--memory', f"{module.params['memory']}G",
            '--core-fraction', str(module.params['core_fraction']),
            '--image-family', module.params['image_family'],
            '--disk-size', str(module.params['disk_size']),
            '--network-interface', f"subnet-id={module.params['subnet_id']},nat-ip-version=ipv4",
            '--format', 'json',
        ]
        if module.params['preemptible']:
            cmd.append('--preemptible')
        if module.params['ssh_public_key']:
            cmd.extend(['--metadata', f"ssh-keys=ubuntu:{module.params['ssh_public_key']}"])

        create_out = run_yc(cmd, module)
        inst = json.loads(create_out)
        result['instance_id'] = inst.get('id', '')
        result['changed'] = True
        nics = inst.get('network_interfaces', [])
        if nics and nics[0].get('primary_v4_address', {}).get('one_to_one_nat', {}).get('address'):
            result['external_ip'] = nics[0]['primary_v4_address']['one_to_one_nat']['address']

    elif state == 'absent':
        if not existing:
            module.exit_json(**result)
        run_yc(['yc', 'compute', 'instance', 'delete', '--id', existing[0]['id']], module)
        result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
