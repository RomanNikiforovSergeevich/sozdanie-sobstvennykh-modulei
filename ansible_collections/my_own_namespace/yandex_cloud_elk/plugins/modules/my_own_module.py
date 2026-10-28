#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_own_module
short_description: Creates a text file on remote host
version_added: "1.0.0"
description:
    - This module creates a text file with specified content at the given path.
    - If the file already exists with the same content, no changes are made (idempotent).
options:
    path:
        description: Path where the file should be created.
        required: true
        type: str
    content:
        description: Content to write into the file.
        required: true
        type: str
author:
    - Roman Nikiforov (@RomanNikiforovSergeevich)
'''

EXAMPLES = r'''
# Create a simple text file
- name: Create hello world file
  my_own_namespace.yandex_cloud_elk.my_own_module:
    path: /tmp/hello.txt
    content: "Hello, World!"

# Create file with multi-line content
- name: Create multi-line file
  my_own_namespace.yandex_cloud_elk.my_own_module:
    path: /tmp/multi.txt
    content: |
      Line 1
      Line 2
      Line 3
'''

RETURN = r'''
path:
    description: Path of the created file.
    type: str
    returned: always
    sample: /tmp/hello.txt
changed:
    description: Whether the file was created or modified.
    type: bool
    returned: always
    sample: true
'''

import os
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        path=dict(type='str', required=True),
        content=dict(type='str', required=True),
    )

    result = dict(
        changed=False,
        path='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    path = module.params['path']
    content = module.params['content']
    result['path'] = path

    if module.check_mode:
        module.exit_json(**result)

    file_exists = os.path.exists(path)
    current_content = ''
    if file_exists:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                current_content = f.read()
        except Exception as e:
            module.fail_json(msg=f"Failed to read existing file: {e}", **result)

    if not file_exists or current_content != content:
        try:
            parent_dir = os.path.dirname(path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            result['changed'] = True
        except Exception as e:
            module.fail_json(msg=f"Failed to write file: {e}", **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
