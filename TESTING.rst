..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.


      Convention for heading levels in the devref:
      =======  Heading 0 (reserved for the title in a document)
      -------  Heading 1
      ~~~~~~~  Heading 2
      +++++++  Heading 3
      '''''''  Heading 4
      (Avoid deeper levels because they do not render well.)

.. _testing_net_ansible:


Testing Networking Ansible
==========================

Here you can find guidelines to help you understand testing structure of
networking-ansible project. Currently we have in-tree unittests and integration
tests using Tempest framework. Each target different way of testing the
production code.

Unittests
~~~~~~~~~

Unittests aim to white-box test the code mocking bottom layers of the project.
The files containing tests are placed under ``networking_ansible/tests/unit``
directory. Each test file name corresponds with Python module that is under
tests, the testing module has a ``test_`` prefix. For example, module
``networking_ansible/foo/bar/baz.py`` should have a testing module
``networking_ansible/tests/unit/foo/bar/test_baz.py``. The directory structure
is automatically checked by the pep8 tox target.

Integration tempest tests
~~~~~~~~~~~~~~~~~~~~~~~~~
TODO(jlibosva): Write here something when feeling lonely.
