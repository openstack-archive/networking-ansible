.. _api:

==========
Python API
==========

Networking-Ansible can be called directly via python API. This method does not
require a running OpenStack, with neutron.

In this section, this use case will be exercised in a set of example commands to
show how end users could import the networking-ansible API and call it to
execute switch level network configuration.

#. In a python environment import the networking-ansible class.

  .. code-block:: console

    from networking_ansible.api import NetworkingAnsible

#. Instantiate the NetworkingAnsible class. This requires a dictionary that
   represents an Ansible Inventory data structure. This data structure could be
   read from a file or built dynamically by the code that is instantiating the
   class. This example will statically assign the data structure to a variable
   to show the expected data structure.

  .. code-block:: console

    inventory = {'all':
      {'hosts':
        {'examplehost': 
          {'ansible_network_os=openswitch,
           'ansible_host=5.6.7.8,
           'ansible_user=ansible,
           'ansible_ssh_pass=password,
          }
        }
      }
    }
    net_ans = NetworkingAnsible(inventory)

#. Call functions to configure the inventory.

  .. code-block:: console

    vlan = 37
    net_ans.create_network(vlan)
