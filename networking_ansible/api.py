# Copyright (c) 2018 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import ansible_runner

from networking_ansible import exceptions


class NetworkingAnsible(object):
    """Object to invoke ansible_runner to call Ansible Networking

    Hold inventory and provide an interface for calling
    roles in Ansible Networking to manipulate switch configuration
    """

    def __init__(self, inventory):
        self.inventory = inventory

    def _run_task(self, task, hostname, port=None, vlan_id=None):
        """Run a task.

        :param task: name of task in openstack-ml2 ansible role
        :param host_name: name of a host defined in ml2 conf ini files
        :param segmentation_id: vlan id of the network
        :param switch_port: port name on the switch (optional)

        See etc/ansible/roles/openstack-ml2/README.md for an exmaple playbook
        """

        # build out the ansible playbook
        playbook = [{
            'name': 'Openstack networking-ansible playbook',
            'hosts': hostname,
            'gather_facts': 'no',  # no need to gather facts every run
            'tasks': [{
                'name': 'do {}'.format(task),
                'import_role': {
                    'name': 'openstack-ml2',
                    'tasks_from': task,
                },
                'vars': {
                    'segmentation_id': vlan_id,
                }
            }]
        }]
        if port:
            playbook[0]['tasks'][0]['vars']['port_name'] = port
            playbook[0]['tasks'][0]['vars']['port_description'] = port

        # invoke ansible networking via ansible runner
        result = ansible_runner.run(playbook=playbook,
                                    inventory=self.inventory,
                                    settings={'pexpect_use_poll': False})
        # check for failure
        if result.status == 'failed' or \
                (result.stats and result.stats.get('failures', [])):
            raise exceptions.AnsibleRunnerException(' '.join(result.stdout))
        return result

    def create_vlan(self, hostname, vlan_id):
        return self._run_task('create_vlan', hostname, vlan_id=vlan_id)

    def delete_vlan(self, hostname, vlan_id):
        return self._run_task('delete_vlan', hostname, vlan_id=vlan_id)

    def update_access_port(self, hostname, port, vlan_id):
        """Configure access port on a vlan or shutdown the port.

        If the configuration required to unplug the port is not present
        (e.g. local link information), the port will not be unplugged and no
        exception will be raised.

        :param hostname: The name of the host in Ansible inventory.
        :param port: The port to configure.
        :param lan_id: The vlan_id to assign to the port.
                       An empty is will get translated in Ansible to the
                       target device's default VLAN assignment.
        """
        return self._run_task('update_access_port', hostname, port, vlan_id)

    def delete_port(self, hostname, port):
        return self._run_task('delete_access_port', hostname, port)
