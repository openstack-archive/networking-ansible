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

from neutron_lib.plugins.ml2 import api
from oslo_log import log as logging

from networking_ansible import config
from networking_ansible.trunk import trunk_driver

LOG = logging.getLogger(__name__)

class AnsibleMechanismDriver(api.MechanismDriver):
    """
    ML2 Mechanism Driver for Ansible Networking
    https://www.ansible.com/integrations/networks
    """

    def initialize(self):
        LOG.debug("Initializing Ansible ML2 driver")
        self.trunk_driver = trunk_driver.AnsibleTrunkDriver.create()
        self.inventory = config.build_ansible_inventory()

    def run_task(self, network, host_name, task):
        """
        task is a dictionary that represents an ansible task.
        # TODO: this probably needs to be a function on a switch object
                once we get that far
        """
        playbook = [{
            'name': 'Openstack networking-ansible playbook',
            'hosts': host_name,
            'tasks': [task]
        }]

        result = ansible_runner.run(ident=network['id'],
                                    playbook=playbook,
                                    inventory=self.inventory)
        failures = result.stats['failures']
        if failures:
            # TODO: Should this be a custom error rather than Exception?
            raise Exception(failures)
        return result

    def create_network_postcommit(self, context):
        """Create a network.
        :param context: NetworkContext instance describing the new
        network.
        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Raising an exception will
        cause the deletion of the resource.
        """

        network = context.current
        network_id = network['id']
        provider_type = network['provider:network_type']
        segmentation_id = network['provider:segmentation_id']
        physnet = network['provider:physical_network']


        if provider_type == 'vlan' and segmentation_id:
            # assuming all hosts
            # TODO: can we filter by physnets?
            for host_name in inventory['all']['hosts']:
                # Create VLAN on the switch
                try:
                    task = {'name': 'add vlan id {}'.format(segmentation_id),
                           # TODO: This is hard coded for juniper because
                           #       that was the initial vm we got running.
                            'junos_vlan': {'name': 'vlan{}'.format(
                                                       segmentation_id),
                                           'vlan_id': segmentation_id}
                           }

                    result = self.run_task(network, host_name, task)
                    LOG.info('Network {net_id} has been added on ansible host '
                             '{host}'.format(net_id=network['id'],
                                             host=host_name))

                except Exception as e:
                    LOG.error('Failed to create network {net_id} '
                              'on ansible host: {host}, '
                              'reason: {err}'.format(net_id=network_id,
                                                       host=host_name,
                                                       err=e))

    def delete_network_postcommit(self, context):
        """Delete a network.
        :param context: NetworkContext instance describing the current
        state of the network, prior to the call to delete it.
        Called after the transaction commits. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance. Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """

        network = context.current
        provider_type = network['provider:network_type']
        segmentation_id = network['provider:segmentation_id']
        physnet = network['provider:physical_network']

        if provider_type == 'vlan' and segmentation_id:
            # assuming all hosts
            # TODO: can we filter by physnets?
            for host_name in inventory['all']['hosts']:
                # Delete VLAN on the switch
                try:
                    task = {'name': 'delete vlan id {}'.format(
                                        segmentation_id),
                           # TODO: This is hard coded for juniper because
                           #       that was the initial vm we got running.
                            'junos_vlan': {'name': 'vlan{}'.format(
                                                       segmentation_id),
                                           'state': 'absent'}
                           }

                    result = self.run_task(network, host_name, task)
                    LOG.info('Network {net_id} has been deleted on ansible '
                             'host {host}'.format(net_id=network['id'],
                                                  host=host_name))

                except Exception as e:
                    LOG.error('Failed to delete network {net_id} '
                              'on ansible host: {host}, '
                              'reason: {err}'.format(net_id=network['id'],
                                                     host=host_name,
                                                     err=e))

    def update_port_postcommit(self, context):
        """Update a port.
        :param context: PortContext instance describing the new
        state of the port, as well as the original state prior
        to the update_port call.
        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Raising an exception will
        result in the deletion of the resource.
        update_port_postcommit is called for all changes to the port
        state. It is up to the mechanism driver to ignore state or
        state changes that it does not know or care about.
        """
        LOG.info("Ansible ML2 driver: update_port_postcommit")


    def delete_port_postcommit(self, context):
        """Delete a port.
        :param context: PortContext instance describing the current
        state of the port, prior to the call to delete it.
        Called after the transaction completes. Call can block, though
        will block the entire process so care should be taken to not
        drastically affect performance.  Runtime errors are not
        expected, and will not prevent the resource from being
        deleted.
        """
        LOG.info("Ansible ML2 driver: delete_port_postcommit")

    def bind_port(self, context):
        """Attempt to bind a port.
        :param context: PortContext instance describing the port
        This method is called outside any transaction to attempt to
        establish a port binding using this mechanism driver. Bindings
        may be created at each of multiple levels of a hierarchical
        network, and are established from the top level downward. At
        each level, the mechanism driver determines whether it can
        bind to any of the network segments in the
        context.segments_to_bind property, based on the value of the
        context.host property, any relevant port or network
        attributes, and its own knowledge of the network topology. At
        the top level, context.segments_to_bind contains the static
        segments of the port's network. At each lower level of
        binding, it contains static or dynamic segments supplied by
        the driver that bound at the level above. If the driver is
        able to complete the binding of the port to any segment in
        context.segments_to_bind, it must call context.set_binding
        with the binding details. If it can partially bind the port,
        it must call context.continue_binding with the network
        segments to be used to bind at the next lower level.
        If the binding results are committed after bind_port returns,
        they will be seen by all mechanism drivers as
        update_port_precommit and update_port_postcommit calls. But if
        some other thread or process concurrently binds or updates the
        port, these binding results will not be committed, and
        update_port_precommit and update_port_postcommit will not be
        called on the mechanism drivers with these results. Because
        binding results can be discarded rather than committed,
        drivers should avoid making persistent state changes in
        bind_port, or else must ensure that such state changes are
        eventually cleaned up.
        Implementing this method explicitly declares the mechanism
        driver as having the intention to bind ports. This is inspected
        by the QoS service to identify the available QoS rules you
        can use with ports.
        """
        LOG.info("Ansible ML2 driver: bind_port")
