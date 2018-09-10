=============================
Networking-Ansible ML2 Driver
=============================

Overview
--------
Networking-Ansible is a python library that abstracts management and
interaction with switching hardware to Ansible Networking. This library is not
tested with all the modules included with Ansible Networking. In theory it
should work with any switch that has compatible modules included with Ansible
Networking if the provider tasks are added to this library's Ansible role.
See the contributor documentation for more information
about adding support for an Ansible Networking driver to the openstack-ml2
Ansible role.

* Free software: Apache license
* Documentation: https://networking-ansible.readthedocs.io/en/latest/
* Source: https://git.openstack.org/cgit/openstack/networking-ansible/
* Bugs: https://storyboard.openstack.org/#!/project/openstack/networking-ansible/

Components
----------
The Networking-Ansible library consists of the following components:

``ML2 Mechanism Driver``
  Invoked by neutron to configure L2 networking for OpenStack tenant networks.

``Python API``
  Imported directly by python.

Use Cases
---------
``OpenStack Ironic Baremetal Guest Deployment``

Ironic uses Networking-Ansible to configure the switch ports for the baremetal guests.
Ironic needs to swap the port a baremetal guest is connected to between the
Ironic provisioning network and the tenant VLAN that the guest is assigned.

``Python API``

Any python application could need the ability to communicate with a switch
to perform a task that networking-ansible is able to complete. The interaction
with ansible is designed in a library style that will allow direct import and
invocation in python independant of a running OpenStack deployment.

Features
--------

* Create and delete VLANs
* Configure a port in access mode and assign a it to a VLAN
