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

from neutron_lib.plugins.ml2 import api
from oslo_log import log as logging

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
