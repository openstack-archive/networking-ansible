.. _install-rdo:

Install and configure for Red Hat Enterprise Linux and CentOS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


This section describes how to install and configure the Ansible Networking ML2 Driver
for Red Hat Enterprise Linux 7 and CentOS 7.

.. include:: common_prerequisites.rst

Install and configure components
--------------------------------

#. Install the packages:

   .. code-block:: console

      # yum install networking-ansible

.. include:: common_configure.rst

Finalize installation
---------------------

Restart the neutron-server service:

.. code-block:: console

   # systemctl restart neutron-server.service
