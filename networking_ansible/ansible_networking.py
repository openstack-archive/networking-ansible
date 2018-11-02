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
from oslo_log import log as logging

from networking_ansible import exceptions

LOG = logging.getLogger(__name__)


class AnsibleNetworking(object):
    """Object to invoke ansible_runner to call Ansible Networking

    Hold inventory and provide an interface for calling
    roles in Ansible Networking to manipulate switch configuration
    """

    def __init__(self, inventory):
        self.inventory = inventory
        # create a dict of switches that have macs defined
        # dict uses mac for key and name for value
        hosts = inventory['all']['hosts']
        self.mac_map = {
            h['mac'].upper(): name for name, h in hosts.items() if 'mac' in h
        }

    def _run_task(self, task, host_name, segmentation_id, switch_port=None):
        """Run a task.

        :param task: name of task in openstack-ml2 ansible role
        :param host_name: name of a host defined in ml2 conf ini files
        :param segmentation_id: vlan id of the network
        :param switch_port: port name on the switch (optional)

        See etc/ansible/roles/openstack-ml2/README.md for an exmaple playbook
        """
        # TODO(radez): This is hard coded for juniper because
        #       that was the initial vm we got running.
        #       need to find out how to do this cross vendor
        if segmentation_id == '1':
            segmentation_name = 'default'
        else:
            segmentation_name = 'vlan{}'.format(segmentation_id)

        # build out the ansible playbook
        playbook = [{
            'name': 'Openstack networking-ansible playbook',
            'hosts': host_name,
            'gather_facts': 'no',  # no need to gather facts every run
            'tasks': [{
                'name': 'do {}'.format(task),
                'import_role': {
                    'name': 'openstack-ml2',
                    'tasks_from': task,
                },
                'vars': {
                    'segmentation_name': segmentation_name,
                    'segmentation_id': segmentation_id,
                }
            }]
        }]
        if switch_port:
            playbook[0]['tasks'][0]['vars']['port_name'] = switch_port
            playbook[0]['tasks'][0]['vars']['port_description'] = switch_port

        # TODO(radez) should we pass ident?
        result = ansible_runner.run(playbook=playbook,
                                    inventory=self.inventory,
                                    settings={'pexpect_use_poll': False})
        if result.status == 'failed' or \
                (result.stats and result.stats.get('failures', [])):
            raise exceptions.AnsibleRunnerException(' '.join(result.stdout))
        return result

    def create_network(self, host_name, segmentation_id):
        self._run_task('create_network', host_name, segmentation_id)

    def delete_network(self, host_name, segmentation_id):
        self._run_task('delete_network', host_name, segmentation_id)

    def vlan_access_port(self, assign_remove, port, network):
        """Assign an access port to a vlan.

        If the configuration required to unplug the port is not present
        (e.g. local link information), the port will not be unplugged and no
        exception will be raised.

        :param assign_remove: 'assign' or 'remove'
        :param port: The port to unplug
        :param network: The network from which to unplug the port
        """
        task = {'assign': 'update_port',
                'remove': 'delete_port'}
        debug_msg = {'assign': 'Plugging in port {switch_port} on '
                               '{switch_name} to vlan: {segmentation_id}',
                     'remove': 'Unplugging port {switch_port} on '
                               '{switch_name} from vlan: {segmentation_id}'}
        info_msg = {'assign': 'Port {neutron_port} has been plugged into '
                              'network {net_id} on device {switch_name}',
                    'remove': 'Port {neutron_port} has been unplugged from '
                              'network {net_id} on device {switch_name}'}
        error_msg = {'assign': 'Failed to unplug port {neutron_port} on '
                               'device: {switch_name} from network {net_id} '
                               'reason: {exc}',
                     'remove': 'Failed to plug in port {neutron_port} on '
                               'device: {switch_name} from network {net_id} '
                               'reason: {exc}'}

        # If segmentation ID is None, set vlan 1
        segmentation_id = network['provider:segmentation_id'] or '1'

        local_link_info = port['binding:profile'].get('local_link_information')
        if not local_link_info:
            return
        switch_mac = local_link_info[0].get('switch_id', '').upper()
        switch_name = local_link_info[0].get('switch_info')
        switch_port = local_link_info[0].get('port_id')
        # fill in the switch name if mac exists but name is not defined
        # this provides support for introspection when the switch's mac is
        # also provided in the ML2 conf for ansible-networking
        if not switch_name and switch_mac in self.mac_map:
            switch_name = self.mac_map[switch_mac]
        try:
            LOG.debug(debug_msg[assign_remove].format(
                switch_port=switch_port,
                switch_name=switch_name,
                segmentation_id=segmentation_id))
            self._run_task(task[assign_remove], switch_name,
                           segmentation_id, switch_port)
            LOG.info(info_msg[assign_remove].format(
                neutron_port=port['id'],
                net_id=network['id'],
                switch_name=switch_name))
        except Exception as e:
            LOG.error(error_msg[assign_remove].format(
                neutron_port=port['id'],
                net_id=network['id'],
                switch_name=switch_name,
                exc=e))
            raise
