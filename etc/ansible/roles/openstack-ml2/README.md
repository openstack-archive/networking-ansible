openstack-ml2
=============
This role implements network device configuration for OpenStack Neutron ML2.

Requirements
------------
* OpenStack Neutron ML2 networking-ansible

Role Variables
--------------

* junos_enable_netconf

* vlan_id
* vlan_name (default depends on provider)

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in
regards to parameters that may need to be set for other roles, or variables
that are used from other roles.

Example Playbook
----------------

```
---
- hosts: all

  tasks:
    - name: do create_vlan
      import_role:
        name: openstack-ml2
        tasks_from: create_vlan
      vars:
        vlan_name: v101
        vlan_id: 101

    - name: do create_vlan
      import_role:
        name: openstack-ml2
        tasks_from: delete_vlan
      vars:
        vlan_id: 101
        vlan_name: v101
```


License
-------
Apache

Author Information
------------------
Ansible
