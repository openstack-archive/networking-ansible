.. _install-ubuntu:

Install and configure for Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section describes how to install and configure the Ansible Networking ML2 Driver
for Ubuntu 14.04 (LTS).

.. include:: common_prerequisites.rst

Install and configure components
--------------------------------

#. Install the packages:

   .. code-block:: console

      # apt-get update

      # apt-get install networking-ansible

.. include:: common_configure.rst

Finalize installation
---------------------

Restart the neutron-server service:

.. code-block:: console

   # service neutron-server restart
