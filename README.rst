=============================
Networking-Ansible ML2 Driver
=============================

Overview
--------
Networking-Ansible is a Neutron ML2 driver that abstracts the interaction with
switch hardware to Ansible Networking. This driver may not be tested with all
the modules included with Ansible Networking. In theory it should work with any
switch that has compatible modules included with Ansible Networking.

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
Ironic Baremetal Guests

Features
--------

* On create network a vlan can be defined
* On port update will assign a vlan to an access port
