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

from neutron.plugins.ml2.common import exceptions as ml2_exc
from neutron_lib._i18n import _
from neutron_lib import exceptions


class NetworkingAnsibleMechException(ml2_exc.MechanismDriverError):
    def __init__(self, message):
        super(NetworkingAnsibleMechException, self).__init__(message)


class LocalLinkInfoMissingException(exceptions.NeutronException):
    message = _('%(stdout)s')

    def __init__(self, message):
        super(LocalLinkInfoMissingException, self).__init__(stdout=message)
