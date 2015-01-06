#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# engine_page.py - Copyright (C) 2012 Red Hat, Inc.
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
from ovirt.node import plugins, valid, ui, utils, app
from ovirt.node.config.defaults import NodeConfigFileSection, ConfigFile, SimpleProvider
from ovirt.node.plugins import Changeset
import setup
import logging
import os
import sys
import traceback
import httplib
import ovirtnode.ovirtfunctions as _functions
import types
import re
import tempfile

import des
import get_hardwareid
import ConfigParser as configparser
from ovirt.node.utils import fs, storage
"""
Configure Engine
"""
import gettext
from otopi import common
_ = lambda m: gettext.dgettext(message=m, domain='otopi')


LOGGER = logging.getLogger(__name__)


class Plugin(plugins.NodePlugin):
    _cert_path = None
    _server = None
    _port = None
    _model_extra = {}
    _pass = {
        "engine_cfg.httpPORT":"",
        "engine_cfg.httpsPORT": "", 
        "engine_cfg.authPASS":"",
        "engine_cfg.authPASS_confirmation":"",
        "engine_cfg.orgNAME": "",
        "engine_cfg.hostFQDN": "",
        "engine_cfg.adminPASS":"",
        "engine_cfg.adminPASS_confirmation":"",
        "engine_cfg.isoPATH": "",
        "engine_cfg.license":"", 
    }
    #_model = [("virtulization", "Virtul"),
    #          ("gluster", "Gluster"),
    #          ("both", "Both")
    #          ]
    #_storage = [("nfs","NFS"),
    #            ("fc","FC"),
    #            ("iscsi","ISCSI"),
    #            ("posixfs","POSIXFS")
    #            ]
    #_db_type = [("remote","Remote"),
    #            ("local","Local")
    #            ]
    #_iso_domain = [("yes","Yes"),
    #               ("no","No")
    #               ]
    #_firewall = [("none","None"),
    #             ("iptables","IPTables")
    #             ]

    def __init__(self, app):
        super(Plugin, self).__init__(app)

            # Keys/Paths to widgets related to NIC settings
        self._options_details_group = self.widgets.group([
            "engine_cfg.model",
            "engine_cfg.isoASK",
            "engine_cfg.dbTYPE",
            "engine_cfg.firewall",
            "engine_cfg.storage",
        ])

        #if os.path.isfile("/var/lib/ovirt-engine/setup/answers/20141230143138-setup.conf"):
            #_functions.system_closefds("sed -i 1d /var/lib/ovirt-engine/setup/answers/20141230143138-setup.conf &> /dev/null")
        #else :
            #_functions.system_closefds("engine-setup --gen-answer-file=/var/lib/ovirt-engine/setup/answers/20141230143138-setup.conf &> /dev/null")
            #_functions.system_closefds("sed -i 1d /var/lib/ovirt-engine/setup/answers/20141230143138-setup.conf &> /dev/null")
        import os
        
        
        fn = os.path.dirname(__file__)
        first_level=os.path.dirname(fn)
        sec_level=os.path.dirname(first_level)
        #third_level=os.path.dirname()
        fn=os.path.abspath(os.path.join(sec_level,"20141230183208-setup.conf"))
        self.fn=fn

        cfgfile = ConfigFile(fn, EngineCfgProvider)
        self.logger.info("engine configure file: %s" % fn)
        self.engine_config = EngineConfig(cfgfile)
        self.logger.info("retrieve conf %s " % fn)

    def name(self):
        return "Engine"

    def rank(self):
        return 100

    def model(self):

        self.cfg = self.engine_config.retrieve()
        #self.logger.info("cfg[HTTP_PORT] %s !" % cfg['http_port'])

        model = {

            "engine_cfg.httpPORT": self.cfg["OVESETUP_CONFIG/httpPort"] or "80",
            "engine_cfg.httpsPORT": self.cfg["OVESETUP_CONFIG/httpsPort"] or "443",
            "engine_cfg.hostFQDN":self.cfg["OVESETUP_CONFIG/fqdn"] or "localhost.localdomain",
            "engine_cfg.license":self.cfg['ORG_LICENSE'] or "",
            "engine_cfg.isoPATH":self.cfg['OVESETUP_CONFIG/isoDomainMountPoint'] or "",
            "engine_cfg.authPASS":self.cfg["OVESETUP_CONFIG/adminPassword"] or "",
            "engine_cfg.authPASS_confirmation":self.cfg["OVESETUP_CONFIG/adminPassword"] or "",
            "engine_cfg.orgNAME":self.cfg["OVESETUP_PKI/organization"] or "localdomain",
            "engine_cfg.adminPASS":self.cfg["OVESETUP_DB/password"] or "",
            "engine_cfg.adminPASS_confirmation" : self.cfg["OVESETUP_DB/password"] or "",

        }
        model.update(self._model_extra)
        return model
        #return model

    def validators(self):
        same_as_password = plugins.Validator.SameAsIn(self,
                                                      "engine_cfg.authPASS",
                                                      "Password")
        same_as_password1 = plugins.Validator.SameAsIn(self,
                                                       "engine_cfg.adminPASS",
                                                       "Password")
        def cert_validator(v):

            pass
                #return  ("The Engine Certificate does not exist. " +
                #                   "Retrieve and verify it before you " +
                #                   "continue.")

        return {
            #        "engine_cfg.httpPORT": valid.Port(),
            #        "engine_cfg.httpsPORT": valid.Port(),
            #        "engine_cfg.authPASS": valid.Text()| valid.Empty(),
            #        "engine_cfg.authPASS_confirmation": same_as_password,
            #        "engine_cfg.adminPASS": valid.Text()| valid.Empty(),
            #        "engine_cfg.adminPASS_confirmation": same_as_password1,
            #        "action.register": cert_validator,
            #        "engine_cfg.license": valid.validator_license() | valid.Empty(),
        }

    def ui_content(self):
        port_widgets = [ui.Entry("engine_cfg.httpPORT", "HTTP Port:"),
                        ui.Entry("engine_cfg.httpsPORT", "HTTPS Port:")
                        ]

        authpasswd_widgets = [ui.PasswordEntry("engine_cfg.authPASS", "Admin passwd:"),
                              ui.PasswordEntry("engine_cfg.authPASS_confirmation", "Re passwd:")
                              ]
        license_widgets = [ui.Entry("engine_cfg.orgNAME", "Org Name:"),
                           ui.Entry("engine_cfg.hostFQDN", "Domain name:")
                           ] 
        adminpasswd_widgets = [ui.PasswordEntry("engine_cfg.adminPASS", "DB passwd:"),
                               ui.PasswordEntry("engine_cfg.adminPASS_confirmation", "Re passwd:")
                               ]  
        #domain_widgets = [
        #                  ] 
        #options_widgets = [ui.Options("engine_cfg.dbTYPE","DB type:", self._db_type),
        #                   ui.Options("engine_cfg.firewall","Firewall:",self._firewall)
        #                   ]                                                                               

        ws = [ui.Header("header[0]", "Engine Configuration"),
              ui.Row("row[0]", port_widgets),

              ui.Row("row[1]", authpasswd_widgets),
              #ui.Row("row[2]", license_widgets),
              ui.Entry("engine_cfg.orgNAME", "Org Name:"),
              ui.Entry("engine_cfg.hostFQDN", "Domain name:"),
              #ui.Row("row[3]", domain_widgets),
              ui.Row("row[3]", adminpasswd_widgets),
              ui.Entry("engine_cfg.isoPATH","ISO path:",align_vertical=True),
              ui.Entry("engine_cfg.license", "Org License:",align_vertical=True),
              ui.Divider("divider[1]"),
              ui.ErrorLabel("engine_cfg.infomation", "infomatoin:"),
              ui.Divider("divider[2]"),
              #ui.Options("engine_cfg.model","App modes:", self._model),
              #ui.Options("engine_cfg.storage","Storage:", self._storage),

              #ui.Options("engine_cfg.isoASK","NFS ISO Domain:",self._iso_domain),
              #ui.Options("engine_cfg.dbTYPE","DB type:", self._db_type),
              #ui.Options("engine_cfg.firewall","Firewall:",self._firewall),

              #ui.Entry("vdsm_cfg.address", "Management Server:"),
              #ui.Entry("vdsm_cfg.port", "Management Server Port:"),
              #ui.Divider("divider[0]"),
              ui.Row("row[4]",[ui.Button("action.fetch_options", "Advance options"),
                               ui.Button("action.reset", "Reset")]),
              ui.Divider("divider[3]"),
              ui.Button("action.register", "save & engine-setup")
              #ui.KeywordLabel("vdsm_cfg.cert", "Certificate Status: "),
              #ui.Divider("divider[1]"),
              #ui.Label("vdsm_cfg.password._label",
              #         "Optional password for adding Node through oVirt " + 
              #         "Engine UI"),
              #ui.PasswordEntry("vdsm_cfg.password", "Password:"),
              #ui.PasswordEntry("vdsm_cfg.password_confirmation",
              #                 "Confirm Password:"),
              ]
        #if os.path.exists("/etc/pki/ovirt-engine/keys/engine.p12"):
        #    self._model_extra("engine_cfg.httpPORT").enabled(False)
        #    self._model_extra("engine_cfg.httpsPORT").enabled(False)
        #    self._model_extra("engine_cfg.authPASS").enabled(False)
        #    self._model_extra("engine_cfg.authPASS_confirmation").enabled(False)
        #    self._model_extra("engine_cfg.orgNAME").enabled(False)
        #    self._model_extra("engine_cfg.hostFQDN").enabled(False)
        #    self._model_extra("engine_cfg.adminPASS").enabled(False)
        #    self._model_extra("engine_cfg.adminPASS_confirmation").enabled(False)
        #    self._model_extra("engine_cfg.isoPATH").enabled(False)
        #    self._model_extra("engine_cfg.license").enabled(False)

        page = ui.Page("page", ws)
        #page.buttons = [ui.SaveButton("action.register", "save & engine-setup")]
        page.buttons = [ ]
        self.widgets.add(page)
        return page

    def isstring(self,str):
        self.logger.debug("str:%s" % str)
        if isinstance(str,(float,int)):
            return True
        if str :
            if str.strip() != "":
                return True
            else :
                return False
        else :
            return False
    def validateMountPoint(self,path):
        if not verifyStringFormat(path, "^\/[\w\_\-\s]+(\/[\w\_\-\s]+)*\/?$"):
            self.logger.debug("verifyStringFormat")
            return False
        if _isPathInExportFs(path):
            self.logger.debug("_isPathInExportFs")
            return False
        if os.path.exists(path) and len(os.listdir(path)):
            self.logger.debug("_isPathInExportFs")
            return False
        if not _isPathWriteable(_getBasePath(path)):
            self.logger.debug("_isPathWriteable")
            return False

        return True
    def islicense(self,license):
        is_valid = True
        if len(license) != 32 :
            return False
        name = get_hardwareid.get_hardwareid(license)
        self.logger.debug("lecense : %s key : %s" % (license,valid.desKey))

        if name :
            is_valid = True
        else :
            is_valid = False
        return is_valid

    def on_change(self, changes):
        for path, value in changes.items():
            self.logger.debug("%s: %s" % (path,value))
            if path == "engine_cfg.authPASS" :
                self._pass["engine_cfg.authPASS"] = value
            elif  path == "engine_cfg.authPASS_confirmation" :
                self._pass["engine_cfg.authPASS_confirmation"] = value
            elif path == "engine_cfg.adminPASS":
                self._pass["engine_cfg.adminPASS"] = value
            elif path == "engine_cfg.adminPASS_confirmation" :
                self._pass["engine_cfg.adminPASS_confirmation"] = value
            elif path == "engine_cfg.license" :
                self._pass["engine_cfg.license"] = value
            elif path == "engine_cfg.httpPORT" :
                self._pass["engine_cfg.httpPORT"] = value
            elif path == "engine_cfg.httpsPORT" :
                self._pass["engine_cfg.httpsPORT"] = value
            elif path == "engine_cfg.orgNAME" :
                self._pass["engine_cfg.orgNAME"] = value
            elif path == "engine_cfg.hostFQDN" :
                self._pass["engine_cfg.hostFQDN"] = value
            elif path == "engine_cfg.isoPATH" :
                self._pass["engine_cfg.isoPATH"] = value
            elif path == "engine_cfg.license" :
                self._pass["engine_cfg.license"] = value

        helper = plugins.Changeset(changes)
        enable_buttons = True
        fetch_options = self.widgets["action.fetch_options"]
        save_button = self.widgets["action.register"]
        info_ui = self.widgets["engine_cfg.infomation"]

        http_port = self._pass["engine_cfg.httpPORT"]
        self.logger.debug("http_port:%s %s" % (http_port,enable_buttons))
        if self.isstring(http_port):
            self.logger.debug("catch http_port :%s" % (http_port))
            port = int(http_port)
            if not (port > 0 and port < 65535) :
                if enable_buttons:
                    info_ui.text("http port error!")
                enable_buttons = False

        else :
            self.logger.debug("catch http_port :%s" % (enable_buttons))
            if enable_buttons:
                info_ui.text("http port error!")
            enable_buttons = False

        https_port = self._pass["engine_cfg.httpsPORT"]
        self.logger.debug("https_port:%s %s" % (https_port,enable_buttons))
        if self.isstring(https_port):
            self.logger.debug("catch https_port :%s" % (https_port))
            port = int(https_port)
            if not (port > 0 and port < 65535 and http_port != https_port) :
                self.logger.debug("catch https_port :%s" % (http_port == https_port))
                if enable_buttons:
                    info_ui.text("https port error!")
                enable_buttons = False

        else :
            if enable_buttons:
                info_ui.text("https port error!")
            enable_buttons = False
        auth_pass = self._pass["engine_cfg.authPASS"] 
        reauth_pass = self._pass["engine_cfg.authPASS_confirmation"] 
        #self.widgets["engine_cfg.authPASS"].EngineConfigvalid(False)
        self.logger.debug("auth_pass:%s %s" % (auth_pass,enable_buttons))
        if self.isstring(auth_pass) and self.isstring(reauth_pass) :
            if auth_pass != reauth_pass:
                if enable_buttons:
                    info_ui.text("auth password confirmation error!")
                enable_buttons = False

        else :
            if enable_buttons:
                info_ui.text("auth password confirmation error!")
            enable_buttons = False

        org_name = self._pass["engine_cfg.orgNAME"]
        self.logger.debug("org_name:%s %s" % (org_name,enable_buttons))
        if not self.isstring(org_name):
            if enable_buttons:
                info_ui.text("org name error!")
            enable_buttons = False 

        host_fqdn = self._pass["engine_cfg.hostFQDN"]
        self.logger.debug("host_fqdn:%s %s" % (host_fqdn,enable_buttons))


        admin_pass = self._pass["engine_cfg.adminPASS"]
        readmin_pass = self._pass["engine_cfg.adminPASS_confirmation"]
        self.logger.debug("admin_pass:%s %s" % (admin_pass,enable_buttons))
        if self.isstring(admin_pass) and self.isstring(readmin_pass):
            if admin_pass != readmin_pass:
                if enable_buttons:
                    info_ui.text("db password confirmation error !")
                enable_buttons = False

        else :
            if enable_buttons:
                info_ui.text("db password confirmation error !")
            enable_buttons = False

        iso_path = self._pass["engine_cfg.isoPATH"]
        self.logger.debug("iso_path:%s %s" % (iso_path,enable_buttons))
        if self.isstring(iso_path):
            if not self.validateMountPoint(iso_path):
                if enable_buttons:

                    info_ui.text("may be iso path exist !")
                enable_buttons = False

        else :
            enable_buttons = False
            info_ui.text("Invalid Path Specified !")

        license = self._pass["engine_cfg.license"] 
        #self.logger.debug("license:%s %s" % (license,enable_buttons))
        if self.isstring(license):
            #self.logger.debug("aaaaaaaaaaaaaalicense:%s %s" % (license,enable_buttons))
            if not self.islicense(license):
                self.logger.debug("catch license:%s" % (license))
                if enable_buttons:
                    info_ui.text("license error !")
                enable_buttons = False

        else :
            self.logger.debug("license: %s" % (enable_buttons))
            if enable_buttons:
                info_ui.text("license error !")
            enable_buttons = False
        self.logger.debug("enable buttons %s" % enable_buttons)
        if enable_buttons:
            fetch_options.enabled(True) 
            save_button.enabled(True)
            info_ui.text("")
        else :
            fetch_options.enabled(False) 
            save_button.enabled(False)


    def _advance_configure(self, app_mode,config_nfs,db_type,firewall,dc_type):
        #self.logger.debug("app_mode=%s,dc_type=%s,config_nfs=%s,db_type=%s,firewall=%s,http_port=%s,https_port=%s,\
        #                    http_port=%s,auth_pass=%s,org_name=%s,org_license=%s,nfs_mp=%s,db_local_pass=%s" 
        #                 % (app_mode,dc_type,config_nfs,db_type,firewall,http_port,https_port,
        #                   host_fqdn,auth_pass,org_name,org_license,nfs_mp,db_local_pass))

        piece={"OVESETUP_CONFIG/applicationMode":app_mode,\
               "OVESETUP_SYSTEM/nfsConfigEnabled":config_nfs,\
               "OVESETUP_CONFIG/storageType":dc_type,\
               "OVESETUP_CONFIG/storageIsLocal":db_type,\
               "OVESETUP_CONFIG/firewallManager":firewall}

        if firewall:
            piece.update({"OVESETUP_CONFIG/updateFirewall":True,"OVESETUP_CONFIG/firewallManager":firewall})
        elif firewall== False:
            piece.update({"OVESETUP_CONFIG/updateFirewall":False,"OVESETUP_CONFIG/firewallManager":None})


        self.engine_config.update(**piece)
                #ui.KeywordLabel("vdsm_cfg.cert", "Certificate Status: "),
                #ui.Divider("divider[1]"),
                #ui.Label("vdsm_cfg.password._label",
                #         "Optional password for adding Node through oVirt " + 
                #         "Engine UI"),
                #ui.PasswordEntry("vdsm_cfg.password", "Password:"),
                #ui.PasswordEntry("vdsm_cfg.password_confirmation",
                #                 "Confirm Password:"),
    def on_merge(self, effective_changes):
        self.logger.info("Saving engine stuff")
        changes = Changeset(self.pending_changes(False))
        effective_model = Changeset(self.model())
        effective_model.update(effective_changes)

        self.logger.debug("Changes: %s" % changes)
        self.logger.debug("Effective Model: %s" % effective_model)
        if changes.contains_any(["action.fetch_options"]):

            http_port = effective_model.values_for(["engine_cfg.httpPORT"])[0]
            https_port = effective_model.values_for(["engine_cfg.httpsPORT"])[0]
            auth_pass = effective_model.values_for(["engine_cfg.authPASS"])[0]
            org_license = effective_model.values_for(["engine_cfg.license"])[0]
            host_fqdn = effective_model.values_for(["engine_cfg.hostFQDN"])[0]
            db_local_pass = effective_model.values_for(["engine_cfg.adminPASS"])[0]
            org_name = effective_model.values_for(["engine_cfg.orgNAME"])[0]
            nfs_mp = effective_model.values_for(["engine_cfg.isoPATH"])[0]
            pieces={"OVESETUP_CONFIG/httpPort":http_port,'OVESETUP_CONFIG/httpsPort':\
                                         https_port,"OVESETUP_CONFIG/adminPassword":auth_pass,\
                                         "ORG_LICENSE":org_license,'OVESETUP_DB/password':db_local_pass,\
                                         "OVESETUP_PKI/organization":org_name,'OVESETUP_CONFIG/isoDomainMountPoint':nfs_mp}
            if not auth_pass:
                pieces.update({'TUI_change_admin':False})
            self.engine_config.update(**pieces)

            self._fp_dialog=AdvanceOptionsDialog(self,'Engine Advance Options:',app_mode=self.cfg["OVESETUP_CONFIG/applicationMode"],
                                                 db_type=self.cfg["OVESETUP_CONFIG/storageIsLocal"],
                                                 config_nfs=self.cfg["OVESETUP_SYSTEM/nfsConfigEnabled"],
                                                 firewall=self.cfg["OVESETUP_CONFIG/firewallManager"],
                                                 dc_type=self.cfg["OVESETUP_CONFIG/storageType"])
            return self._fp_dialog
        elif changes.contains_any(["action.reset"]):
            _functions.system_closefds("rm -rf /etc/ovirt-engine/engine-setup.conf &> /dev/null")
            _functions.system_closefds("engine-setup --gen-answer-file=/etc/ovirt-engine/engine-setup.conf &> /dev/null")
            _functions.system_closefds("sed -i 1d /etc/ovirt-engine/engine-setup.conf &> /dev/null")
        elif changes.contains_any(["dialog.options.save"]):
            #LOGGER.debug("dialog.options.save................................!!!!")
            args = effective_model.values_for(self._options_details_group)
            self._advance_configure(*args)
            self._fp_dialog.close()


        if effective_changes.contains_any(["action.register"]):
            self.logger.debug("engine setup")
            #txs += [ActivateVDSM()]
            http_port = effective_model.values_for(["engine_cfg.httpPORT"])[0]

            https_port = effective_model.values_for(["engine_cfg.httpsPORT"])[0]
            auth_pass = effective_model.values_for(["engine_cfg.authPASS"])[0]
            org_license = effective_model.values_for(["engine_cfg.license"])[0]
            host_fqdn = effective_model.values_for(["engine_cfg.hostFQDN"])[0]
            db_local_pass = effective_model.values_for(["engine_cfg.adminPASS"])[0]
            org_name = effective_model.values_for(["engine_cfg.orgNAME"])[0]
            nfs_mp = effective_model.values_for(["engine_cfg.isoPATH"])[0]
            self.cfg=self.engine_config.retrieve()
            if self.cfg['OVESETUP_SYSTEM/nfsConfigEnabled']:
                if not nfs_mp:
                    return
            pieces={"OVESETUP_CONFIG/httpPort":http_port,'OVESETUP_CONFIG/httpsPort':\
                                         https_port,"OVESETUP_CONFIG/adminPassword":auth_pass,\
                                         "ORG_LICENSE":org_license,'OVESETUP_DB/password':db_local_pass,\
                                         "OVESETUP_PKI/organization":org_name,'OVESETUP_CONFIG/isoDomainMountPoint':nfs_mp}            
            if not auth_pass:
                pieces.update({"TUI_change_admin":False})
            self.engine_config.update(**pieces)

            #args = effective_model.values_for(self._options_details_group)
            #self._advance_configure(*args)
            plugin_type = setup.Plugin
            self.cfg=self.engine_config.retrieve()
            plugin_type.environment=self.cfg
            plugin_type.filename=self.fn
            self.application.switch_to_plugin(plugin_type)
            return
        #if len(txs) > 0:
        #    progress_dialog = ui.TransactionProgressDialog("dialog.txs", txs,
        #                                                   self)
        #    progress_dialog.run()

            # VDSM messes with logging, and we just reset it
        #    app.configure_logging()

        # Acts like a page reload
        return self.ui_content()


def findPort(engineServer, enginePort):
    """Function to find the correct port for a given server
    """
    # pylint: disable-msg=E0611,F0401
    sys.path.append('/usr/share/vdsm-reg')
    import deployUtil  # @UnresolvedImport

    from ovirt_config_setup.engine import \
         TIMEOUT_FIND_HOST_SEC  # @UnresolvedImport
    from ovirt_config_setup.engine import \
         compatiblePort  # @UnresolvedImport
    # pylint: enable-msg=E0611,F0401

    compatPort, sslPort = compatiblePort(enginePort)

    LOGGER.debug("Finding port %s:%s with compat %s ssl %s" % 
                 (engineServer, enginePort, compatPort, sslPort))

    deployUtil.nodeCleanup()

    # Build port list to try
    port_cfgs = [(enginePort, sslPort)]
    if compatPort:
        port_cfgs += [(compatPort, sslPort)]
    else:
        port_cfgs += [(enginePort, False)]

    LOGGER.debug("Port configuratoins for engine: %s" % port_cfgs)

    for try_port, use_ssl in port_cfgs:
        LOGGER.debug("Trying to reach engine %s via %s %s" % 
                     (engineServer, try_port, "SSL" if use_ssl else ""))

        is_reachable = False

        try:
            is_reachable = isHostReachable(host=engineServer,
                                           port=try_port, ssl=use_ssl,
                                           timeout=TIMEOUT_FIND_HOST_SEC)
        except Exception:
            LOGGER.debug("Failed to reach engine: %s" % traceback.format_exc())

        if is_reachable:
            LOGGER.debug("Reached engine")
            enginePort = try_port
            break

    if not is_reachable:
        raise RuntimeError("Can't connect to @ENGINENAME@")

    return enginePort


def isHostReachable(host, port, ssl, timeout):
    """Check if a host is reachable on a given port via HTTP/HTTPS
    """
    if ssl:
        Connection = httplib.HTTPSConnection
    else:
        Connection = httplib.HTTPConnection
    Connection(str(host), port=int(port), timeout=timeout).request("HEAD", "/")
    return True


def retrieveCetrificate(engineServer, enginePort):
    """Function to retrieve and store the certificate from an Engine
    """
    fingerprint = None

    # pylint: disable-msg=E0611,F0401
    sys.path.append('/usr/share/vdsm-reg')
    import deployUtil  # @UnresolvedImport
    # pylint: enable-msg=E0611,F0401

    if deployUtil.getRhevmCert(engineServer, enginePort):
        _, _, path = deployUtil.certPaths('')
        fingerprint = deployUtil.generateFingerPrint(path)
    else:
        msgCert = "Failed downloading @ENGINENAME@ certificate"
        raise RuntimeError(msgCert)

    return path, fingerprint


#
#
# Functions and classes to support the UI
#
#
class VDSM(NodeConfigFileSection):
    """Class to handle VDSM configuration in /etc/default/ovirt file

    >>> from ovirt.node.config.defaults import ConfigFile, SimpleProvider
    >>> fn = "/tmp/cfg_dummy"
    >>> cfgfile = ConfigFile(fn, SimpleProvider)
    >>> n = VDSM(cfgfile)
    >>> n.update("engine.example.com", "1234", "p")
    >>> sorted(n.retrieve().items())
    [('cert_path', 'p'), ('port', '1234'), ('server', 'engine.example.com')]
    """
    keys = ("OVIRT_MANAGEMENT_SERVER",
            "OVIRT_MANAGEMENT_PORT",
            "OVIRT_MANAGEMENT_CERTIFICATE")

    @NodeConfigFileSection.map_and_update_defaults_decorator
    def update(self, server, port, cert_path):
        (valid.Empty() | valid.FQDNOrIPAddress())(server)
        (valid.Empty() | valid.Port())(port)

class EngineConfig(NodeConfigFileSection):
    """Class to handle VDSM configuration in /etc/default/ovirt file

    >>> from ovirt.node.config.defaults import ConfigFile, SimpleProvider
    >>> fn = "/tmp/cfg_dummy"
    >>> cfgfile = ConfigFile(fn, SimpleProvider)
    >>> n = EngineConfig(cfgfile)
    >>> n.update("engine.example.com", "1234", "p")
    >>> sorted(n.retrieve().items())
    [('cert_path', 'p'), ('port', '1234'), ('server', 'engine.example.com')]
    """
    keys = (
        "OVESETUP_CONFIG/httpPort",
        "OVESETUP_CONFIG/httpsPort",
        "OVESETUP_CONFIG/fqdn",
        "OVESETUP_CONFIG/adminPassword",
        "OVESETUP_PKI/organization",
        "ORG_LICENSE",
        "OVESETUP_CONFIG/applicationMode",
        "OVESETUP_DB/host",
        "OVESETUP_DB/port",
        "DB_ADMIN",
        "DB_REMOTE_PASS",
        "DB_SECURE_CONNECTION",
        "DB_LOCAL_PASS",
        "NFS_MP",
        "ISO_DOMAIN_NAME",
        "CONFIG_NFS",
        "OVERRIDE_FIREWALL")
    def __init__(self, cfgfile=None):
        super(EngineConfig, self).__init__(cfgfile)


    @NodeConfigFileSection._map_and_update_defaults_decorator
    def update(self,**kwargs):
        pass

    #def update_advance(self,app_mode,dc_type,config_nfs,db_type,firewall):
    #    self.update(None, None, None, None, None, None, None, None, None, app_mode, dc_type, db_type, None, None, None, None, 
    #                        None, None, None, None, config_nfs, firewall)
    #    pass
    def retrieve(self):
        """Returns the config keys of the current component

        Returns:
            A dict with a mapping (arg, value).
            arg corresponds to the named arguments of the subclass's
            configure() method.
        """

        #keys_to_args = self._args_to_keys_mapping(keys_to_args=True)
        cfg = self.defaults.get_dict()

        #model = {}
        #for key in self.keys:
        #    value = cfg[key] if key in cfg else self.none_value
        #    model[keys_to_args[key]] = value
        #assert len(keys_to_args) == len(model)
        return cfg

class EngineCfgProvider(SimpleProvider):
    def __init__(self,filename):
        super(EngineCfgProvider, self).__init__(filename)
        self.environment={}
        self._config = configparser.ConfigParser()
        self._config.optionxform = str
        if not os.path.exists(filename):
            basedir = os.path.dirname(filename)
            if not os.path.exists(basedir):
                os.makedirs(basedir)
            open(filename, 'a').close()



    def get_dict(self):

        self._configFiles = self._config.read(
            [self.filename]
        )

        self._readEnvironment(
            section="environment:default",
            override=False
        )
        #with open("/root/rec",'a+') as f:
            #for k,v in self.environment.items():
                #f.writelines("\n %s : %s \n" %(k,v))
        return self.environment

    def _readEnvironment(self, section, override):
        if self._config.has_section(section):
            for name, value in self._config.items(section):
                try:
                    value = common.parseTypedValue(value)
                except Exception as e:	

                    raise RuntimeError(
                        _(
                            "Cannot parse configuration file key "
                            "{key} at section {section}: {exception}"
                            ).format(
                                key=name,
                                section=section,
                                exception=e,
                            )
                    )
                if override:
                    self.environment[name] = value
                else:
                    self.environment.setdefault(name, value)

    def update(self, new_dict, remove_empty):
        cfg = self.get_dict()
        cfg.update(new_dict)

        for key, value in cfg.items():
            self.logger.debug("updating configuration : %s = %s " % (key,value))
            #if remove_empty and value is None:
            #    del cfg[key]
            if type(value) not in [str,int,unicode,bool,type(None),list,tuple]:
                raise TypeError("The type (%s) of %s is not allowed" %
                                (type(value), key))

        self._write(cfg)		    
    def _write(self, cfg):
        lines = []
        # Sort the dict, looks nicer
        lines.append('[environment:default]')
        for key in sorted(cfg.iterkeys()):
            lines.append('%s=%s:%s' % (key,common.typeName(cfg[key]), cfg[key]))

        contents = "\n".join(lines) + "\n"

        # The following logic is mainly needed to allow an "offline" testing
        config_fs = fs.Config()
        if config_fs.is_enabled():
            os.unlink(self.filename)
            with config_fs.open_file(self.filename, "w") as dst:
                os.fchmod(f.fileno(), 0o600)

                dst.write(contents)
        else:
            try:
                self.logger.debug("configuration filename : %s", self.filename)
                fs.atomic_write(self.filename, contents)
            except Exception as e:
                self.logger.warning("Atomic write failed: %s" % e)
                with open(self.filename, "w") as dst:
                    dst.write(contents)




class SetRootPassword(utils.Transaction.Element):
    title = "Setting root password and starting sshd"

    def __init__(self, password):
        super(SetRootPassword, self).__init__()
        self.password = password

    def commit(self):
        passwd = utils.security.Passwd()
        passwd.set_password("root", self.password)

        sshd = utils.security.Ssh()
        sshd.password_authentication(True)
        sshd.restart()


class ActivateVDSM(utils.Transaction.Element):
    title = "Activating VDSM"

    def commit(self):
        self.logger.info("Connecting to VDSM server")

        # pylint: disable-msg=E0611,F0401
        sys.path.append('/usr/share/vdsm-reg')
        import deployUtil  # @UnresolvedImport

        sys.path.append('/usr/share/vdsm')
        from vdsm import constants  # @UnresolvedImport

        from ovirt_config_setup.engine import \
             write_vdsm_config  # @UnresolvedImport
        # pylint: enable-msg=E0611,F0401

        cfg = VDSM().retrieve()

        # Stopping vdsm-reg may fail but its ok - its in the case when the
        # menus are run after installation
        deployUtil._logExec([constants.EXT_SERVICE, 'vdsm-reg', 'stop'])
        if write_vdsm_config(cfg["server"], cfg["port"]):
            deployUtil._logExec([constants.EXT_SERVICE, 'vdsm-reg',
                                 'start'])

            msgConf = "@ENGINENAME@ Configuration Successfully Updated"
            self.logger.debug(msgConf)
        else:
            msgConf = "@ENGINENAME@ Configuration Failed"
            raise RuntimeError(msgConf)


class SetEnginePassword(utils.Transaction.Element):
    title = "Setting Engine password"

    def commit(self):
        self.logger.info("Setting Engine password")

class AdvanceOptionsDialog(ui.Dialog):
    plugin = None
    _model = [("virtulization", "Virtul"),
              ("gluster", "Gluster"),
              ("both", "Both")
              ]
    _storage = [("nfs","nfs"),
                ("fc","fc"),
                ("iscsi","iscsi"),
                ("posixfs","posixfs"),
                ("glusterfs","glusterfs"),
                
                ]
    _db_type = [(False,"Remote"),
                (True,"Local")
                ]
    _iso_domain = [(True,"Yes"),
                   (False,"No")
                   ]
    _firewall = [(False,"no firewall"),
                 ("firewalld","firewalld")
                 ]
    def __init__(self, plugin,iface,app_mode,config_nfs,db_type,firewall,dc_type):
        super(AdvanceOptionsDialog, self).__init__("dialog.options",iface,[])
        self.plugin = plugin

        #padd = lambda l: l.ljust(14)
        ws = [ui.Options("engine_cfg.model","App modes:", self._model),
              ui.Options("engine_cfg.storage","Storage:", self._storage),
              ui.Options("engine_cfg.isoASK","NFS ISO Domain:",self._iso_domain),
              ui.Options("engine_cfg.dbTYPE","DB type:", self._db_type),
              ui.Options("engine_cfg.firewall","Firewall:",self._firewall),
              ]
        self.plugin._model_extra.update({
            "engine_cfg.firewall": firewall,
            "engine_cfg.model": app_mode or 'both',
            "engine_cfg.storage": dc_type or 'nfs',
            "engine_cfg.isoASK": config_nfs or False,
            "engine_cfg.dbTYPE": db_type,

        })	
        self.plugin.widgets.add(ws)
        self.children = ws
        self.buttons = [ui.SaveButton("dialog.options.save", "Aplly"),
                        ui.CloseButton("dialog.options.close", "Cancel"),
                        ]
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
def _isPathInExportFs(path):
    if not os.path.exists("/etc/exports"):
        return False
    file = open("/etc/exports")
    fileContent = file.readlines()
    file.close()

    for line in fileContent:
        if verifyStringFormat(line, "^%s\s+.+" % (path)):
            return True
    return False

def _isPathWriteable(path):
    try:
        logging.debug("attempting to write temp file to %s" % (path))
        tempfile.TemporaryFile(dir=path)
        return True
    except:
        logging.warning(traceback.format_exc())
        logging.warning("%s is not writeable" % path)
        return False

def _getBasePath(path):
    if os.path.exists(path):
        return path

    # Iterate up in the tree structure until we get an
    # existing path
    return _getBasePath(os.path.dirname(path.rstrip("/")))