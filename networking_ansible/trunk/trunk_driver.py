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

from neutron_lib.api.definitions import portbindings
from neutron_lib.callbacks import registry
from oslo_config import cfg

from neutron.services.trunk import constants as t_cons
from neutron.services.trunk.drivers import base as trunk_base

from networking_ansible import constants as con

@registry.has_registry_receivers
class AnsibleTrunkDriver(trunk_base.DriverBase):

    @property
    def is_loaded(self):
        try:
            return (con.ANSIBLE_ML2_MECH_DRIVER in
                    cfg.CONF.ml2.mechanism_drivers)
        except cfg.NoSuchOptError:
            return False

    @classmethod
    def create(cls):
         return cls(con.ANSIBLE_ML2_MECH_DRIVER,
                    (portbindings.VIF_TYPE_OVS,
                     portbindings.VIF_TYPE_VHOST_USER,),
                    (t_cons.VLAN,),
                    None,
                    can_trunk_bound_port=True)
