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
        return "Add Hostname"

    def rank(self):
        return 90

    def model(self):
        #cfg = defaults.Collectd().retrieve()
        #fn = "/home/mujun/ovirt_config/20141230183208-setup.conf"

        #cfgfile = ConfigFile(fn)        
        #cfg = defaults.Hostname(cfgfile).retrieve()
        cfg = defaults.Hostname().retrieve()
        model = {
            "collectd.ip": cfg['ip'] or '',
            "collectd.hostname":cfg['hostname'] or '',
        }
        return model

    def validators(self):
        fqdn_ip_or_empty = valid.FQDNOrIPAddress() | valid.Empty()
        return {
                "collectd.ip": valid.Empty() | valid.FQDNOrIPAddress(),
                "collectd.hostname": fqdn_ip_or_empty,
                }

    def ui_content(self):
        ws = [ui.Header("header[0]", "Add Hostname"),
              ui.Label("label", "When you don't have a domain , please add your Node hostname to the Engine."),
              ui.Entry("collectd.ip", "Node ip address:"),
              ui.Entry("collectd.hostname", "Node hostname:"),
              ]
        page = ui.Page("page", ws)
        self.widgets.add(page)
        return page

    def on_change(self, changes):
        pass

    def on_merge(self, effective_changes):
        self.logger.debug("Saving hostname page")
        changes = Changeset(self.pending_changes(False))
        effective_model = Changeset(self.model())
        effective_model.update(effective_changes)

        self.logger.debug("Changes: %s" % changes)
        self.logger.debug("Effective Model: %s" % effective_model)

        collectd_keys = ["collectd.ip", "collectd.hostname"]

        txs = utils.Transaction("Add Node hostname to the Engine")

        if changes.contains_any(collectd_keys):
            model = defaults.Hostname()
            model.update(*effective_model.values_for(collectd_keys))
            args = effective_model.values_for(collectd_keys)
            txs += [Hostname(args[0],args[1])]
            txs += model.transaction()

        progress_dialog = ui.TransactionProgressDialog("dialog.txs", txs, self)
        progress_dialog.run()

class Hostname(utils.Transaction.Element):
    title = "Add engine to Windows AD"

    def __init__(self, ip,hostname):
        super(Hostname, self).__init__()
        self.ip = ip
        self.hostname = hostname

    def commit(self):
        _functions.system_closefds("sed -i '/%s %s/d' /etc/hosts" % (self.ip,self.hostname))
        _functions.system_closefds("sed -i '$a\%s %s' /etc/hosts" % (self.ip,self.hostname))
           
