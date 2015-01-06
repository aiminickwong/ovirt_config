#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# monitoring_page.py - Copyright (C) 2012 Red Hat, Inc.
# Written by Fabian Deutsch <fabiand@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.  A copy of the GNU General Public License is
# also available at http://www.gnu.org/copyleft/gpl.html.
from ovirt.node import plugins, ui, valid, utils
from ovirt.node.config import defaults
from ovirt.node.plugins import Changeset
import ovirtnode.ovirtfunctions as _functions

"""
Configure Monitoring
"""


class Plugin(plugins.NodePlugin):
    _model = None

    def name(self):
        return "AD Operation"

    def rank(self):
        return 90

    def model(self):
        cfg = defaults.Collectd().retrieve()
        model = {
            "collectd.address":  cfg["server"] or "",
            "collectd.port": cfg["port"] or "",
        }
        return model

    def validators(self):
        return {
                "collectd.address": valid.Empty() | valid.FQDNOrIPAddress(),
                "collectd.port": valid.Port(),
                }

    def ui_content(self):
        ws = [ui.Header("header[0]", "Add Engine to Window AD"),
              ui.Label("label", "When add your Engine to domain,you can login the Virtual Desktop as normal user."),
              ui.Entry("collectd.address", "Domain:"),
              ui.Entry("collectd.port", "port:"),
              ]
        page = ui.Page("page", ws)
        self.widgets.add(page)
        return page

    def on_change(self, changes):
        pass

    def on_merge(self, effective_changes):
        self.logger.debug("Saving monitoring page")
        changes = Changeset(self.pending_changes(False))
        effective_model = Changeset(self.model())
        effective_model.update(effective_changes)

        self.logger.debug("Changes: %s" % changes)
        self.logger.debug("Effective Model: %s" % effective_model)

        collectd_keys = ["collectd.address", "collectd.port"]

        txs = utils.Transaction("Add engine to Windows AD")

        if changes.contains_any(collectd_keys):
            model = defaults.Collectd()
            model.update(*effective_model.values_for(collectd_keys))
            args = effective_model.values_for(collectd_keys)
            txs += [AD(args[0],args[1])]
            txs += model.transaction()

        progress_dialog = ui.TransactionProgressDialog("dialog.txs", txs, self)
        progress_dialog.run()

class AD(utils.Transaction.Element):
    title = "Add engine to Windows AD"

    def __init__(self, domain,passwd):
        super(AD, self).__init__()
        self.domain = domain
        self.passwd = passwd

    def commit(self):
        _functions.system_closefds("echo %s > /tmp/password" % (self.passwd))
        _functions.system_closefds("engine-manage-domains -action=add -domain=%s \
                        -user=admin -interactive -provider=ActiveDirectory -addPermissions -passwordFile=/tmp/password \
                         &> /dev/null" % (self.domain))
           
