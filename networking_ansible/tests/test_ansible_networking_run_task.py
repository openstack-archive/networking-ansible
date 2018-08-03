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
        mock_ans_runner.run.assert_called_once()

    def test_run_task_w_switchport(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   self.testsegid,
                                   'fake_switchport')
        mock_ans_runner.run.assert_called_once()

    def test_run_task_w_segmentation_id_1(self, mock_ans_runner):
        mock_result = mock_ans_runner.run.return_value
        mock_result.stats = {'failures': []}

        self.mech.ansnet._run_task('fake_task',
                                   self.testhost,
                                   '1',
                                   'fake_switchport')
        mock_ans_runner.run.assert_called_once()

    def test_run_task_failures(self, mock_ans_runner):
        self.assertRaises(exceptions.AnsibleRunnerException,
                          self.mech.ansnet._run_task,
                          'fake_task',
                          self.testhost,
                          self.testsegid,
                          'fake_switchport')
