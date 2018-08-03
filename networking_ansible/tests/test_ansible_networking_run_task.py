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

from mock import patch

from networking_ansible import exceptions
from networking_ansible.tests import base


@patch('networking_ansible.ansible_networking.ansible_runner')
class TestMechDriverRunTask(base.NetworkingAnsibleTestCase):
    def test_run_task_no_switchport(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   self.testsegid)
        # Assert switch_port is not set
        self.assertTrue('port_name' not in
                        mock_ans_runner.run.call_args[1]['playbook'][0]
                                                     ['tasks'][0]['vars']
                        )
        # Assert switch_port is not set
        self.assertTrue('port_description' not in
                        mock_ans_runner.run.call_args[1]['playbook'][0]
                                                     ['tasks'][0]['vars']
                        )

    def test_run_task_w_switchport(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   self.testsegid,
                                   'fake_switchport')
        # Assert switch_port is set
        self.assertEqual(
            mock_ans_runner.run.call_args[1]['playbook'][0]['tasks']
                                         [0]['vars']['port_name'],
            'fake_switchport')
        # Assert switch_port is set
        self.assertEqual(
            mock_ans_runner.run.call_args[1]['playbook'][0]['tasks']
                                         [0]['vars']['port_description'],
            'fake_switchport')

    def test_run_task_w_segmentation_id_1(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   '1',
                                   'fake_switchport')
        # Assert seg name is default
        self.assertEqual(
            mock_ans_runner.run.call_args[1]['playbook'][0]['tasks']
                                         [0]['vars']['segmentation_name'],
            'default')

    def test_run_task_failures(self, mock_ans_runner):
        self.assertRaises(exceptions.AnsibleRunnerException,
                          self.mech.ansnet._run_task,
                          'fake_task',
                          self.testhost,
                          self.testsegid,
                          'fake_switchport')
