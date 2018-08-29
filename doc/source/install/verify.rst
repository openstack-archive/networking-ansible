.. _verify:

Verify operation
~~~~~~~~~~~~~~~~

Verify operation of the networking-ansible ML2 Driver service.

#. Grep the neutron logs for ansible and confirm the driver has been registered and configured.
   root access CLI commands:

   .. code-block:: console

      $ grep ansible /var/log/neutron/server.log
      INFO neutron.plugins.ml2.managers [-] Configured mechanism driver names: ['ansible']
      INFO neutron.plugins.ml2.managers [-] Loaded mechanism driver names: ['ansible']
      INFO neutron.plugins.ml2.managers [-] Registered mechanism drivers: ['ansible']
