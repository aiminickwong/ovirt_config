#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# remote_storage_page.py - Copyright (C) 2012 Red Hat, Inc.
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
from ovirt.node import utils, valid, plugins, ui
from ovirt.node.config import defaults
from ovirt.node.plugins import Changeset
from ovirt.node.utils import storage
import os
import ovirtnode.ovirtfunctions as _functions
import re
"""
Configure Remote Storage
"""


class Plugin(plugins.NodePlugin):
    _model = None

    def name(self):
        return "Local Storage"

    def rank(self):
        return 70

    def model(self):
        icfg = defaults.iSCSI().retrieve()
        #ncfg = defaults.NFSv4().retrieve()
        model = {}
        model["iscsi.initiator_name"] = icfg["name"] or ""
        #model["iscsi.initiator_name"] = ""
        #model["nfsv4.domain"] = ncfg["domain"]
        return model

    def validators(self):
        return {
                #"iscsi.initiator_name": (valid.Empty() | valid.IQN()),
                #"nfsv4.domain": (valid.Empty() | valid.FQDN()),
                }

    def ui_content(self):
        ws = [ui.Header("header", "Local Storage"),
              ui.Entry("iscsi.initiator_name", "Local Storage Path:",
                       align_vertical=True),
              ui.Divider("divider[0]"),
              #ui.Entry("nfsv4.domain", "NFSv4 Domain (example.redhat.com):",
              #         align_vertical=True),
              ]

        page = ui.Page("page", ws)
        self.widgets.add(page)
        return page

    def on_change(self, changes):
        pass
   
    def on_merge(self, effective_changes):
        self.logger.debug("Saving remote storage page")
        changes = Changeset(self.pending_changes(False))
        effective_model = Changeset(self.model())
        effective_model.update(effective_changes)

        self.logger.debug("Changes: %s" % changes)
        self.logger.debug("Effective Model: %s" % effective_model)

        txs = utils.Transaction("make local storage path")

        iscsi_keys = ["iscsi.initiator_name"]
        if changes.contains_any(iscsi_keys):
            
            args = effective_model.values_for(iscsi_keys)
            #model = defaults.iSCSI()
            txs += [createPath(args[0])]
            #args += [None, None, None]  # No target config
            #model.update(*args)
            #txs += model.transaction()

        #nfsv4_keys = ["nfsv4.domain"]
        #if changes.contains_any(nfsv4_keys):
        #    model = defaults.NFSv4()
        #    args = effective_model.values_for(nfsv4_keys)
        #    model.update(*args)
        #    txs += model.transaction()

        progress_dialog = ui.TransactionProgressDialog("dialog.txs", txs, self)
        progress_dialog.run()

def verifyStringFormat(str, matchRegex):
    '''
    Verify that the string given matches the matchRegex.
    for example:
    string: 111-222
    matchRegex: \d{3}-\d{3}
    this will return true since the string matches the regex
    '''
    pattern = re.compile(matchRegex)
    result = re.match(pattern, str)
    if result == None:
        return False
    else:
        return True
        
class createPath(utils.Transaction.Element):
    title = "make local storage path"

    def __init__(self, path):
        super(createPath, self).__init__()
        self.path = path

    def commit(self):
        if not verifyStringFormat(self.path, "^\/[\w\_\-\s]+(\/[\w\_\-\s]+)*\/?$"):
            return 
        if not os.path.exists(self.path):
            _functions.system_closefds("mkdir -p %s" % self.path)
            _functions.system_closefds("chown 36:36 %s" % self.path)
        else :
            _functions.system_closefds("rm -rf %s &> /dev/null" % self.path)
            _functions.system_closefds("mkdir -p %s &> /dev/null" % self.path)
            _functions.system_closefds("chown 36:36 %s &> /dev/null" % self.path)
