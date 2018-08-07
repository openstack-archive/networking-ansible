# Copyright 2018 Red Hat, Inc.
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

from oslo_config import cfg

service_option = cfg.BoolOpt(
    'netansible',
    default=False,
    help='Whether or not Networking Ansbile mech driver is expected to be '
         'available.')

ovs_opt_group = cfg.OptGroup(
    name='net_ansible_openvswitch',
    title='Settings for OVS provider.',
    help='Options group for OVS Ansible provider.')

OVS_GROUP = [
    cfg.StrOpt(
        'ovsdb_connection',
        default='tcp:127.0.0.1:6640',
        help='Connection string to OVSDB.'),
    cfg.StrOpt(
        'switch_name',
        default='ovs_test',
        help='Name of the switch as presented in the networking ansible '
             'config file.'),
    cfg.StrOpt(
        'bridge_name',
        default='net-ans-br',
        help='Name of the bridge which port is attached to.'),
    cfg.StrOpt(
        'port_name',
        default='net-ans-p0',
        help='Name of the port that is being tested'),
]
