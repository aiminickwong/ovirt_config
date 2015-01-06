#
# ovirt-engine-setup -- ovirt engine setup
# Copyright (C) 2013-2014 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Engine Config."""

ENGINE_SYSCONFDIR = '/etc/ovirt-engine'
ENGINE_SERVICE_CONFIG = '/etc/ovirt-engine/engine.conf'
ENGINE_SERVICE_CONFIG_DEFAULTS = '/usr/share/ovirt-engine/services/ovirt-engine/ovirt-engine.conf'
ENGINE_NOTIFIER_SERVICE_CONFIG = '/etc/ovirt-engine/notifier/notifier.conf'
ENGINE_PKIDIR = '/etc/pki/ovirt-engine'
ENGINE_DATADIR = '/usr/share/ovirt-engine'
ENGINE_LOCALSTATEDIR = '/var/lib/ovirt-engine'
ENGINE_LOG = '/var/log/ovirt-engine'
PACKAGE_NAME = 'ovirt-engine'
PACKAGE_VERSION = '3.5.0.1'
DISPLAY_VERSION = '3.5.0.1-1.fc19'
RPM_VERSION = '3.5.0.1'
RPM_RELEASE = '1.fc19'


# vim: expandtab tabstop=4 shiftwidth=4
