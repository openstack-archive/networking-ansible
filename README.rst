=============================
Networking-Ansible ML2 Driver
=============================

Overview
--------
Networking-Ansible is a Neutron ML2 driver that abstracts the management and
interaction with switching hardware to Ansible Networking. This driver is not
tested with all the modules included with Ansible Networking. In theory it
should work with any switch that has compatible modules included with Ansible
Networking if the provider tasks are added to the Ansible openstack-ml2 role
included with this driver. See the contributor documentation for more information
about adding support for an Ansible Networking driver to the openstack-ml2
Ansible role.

* Free software: Apache license
* Documentation: https://networking-ansible.readthedocs.io/en/latest/
* Source: https://git.openstack.org/cgit/openstack/networking-ansible/
* Bugs: https://storyboard.openstack.org/#!/project/openstack/networking-ansible/

Components
----------
The Networking-Ansible ML2 Driver consists of the following components:

``networking_ansible`` ML2 Driver
  Invoked by neutron to configure L2 networking for tenant networks.

Use Cases
---------
``Ironic Baremetal Guest Deployment``

Ironic uses Networking-Ansible to configure the switch ports for the baremetal guests.
Ironic needs to swap the port a baremetal guest is connected to between the
Ironic provisioning network and the tenant VLAN that the guest is assigned.

Features
--------

* On create network a vlan can be defined
* On port update will assign a vlan to an access port
