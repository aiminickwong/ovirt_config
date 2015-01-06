#
# ovirt-engine-setup -- ovirt engine setup
# Copyright (C) 2013 Red Hat, Inc.
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


import base64
import gettext
_ = lambda m: gettext.dgettext(message=m, domain='ovirt-engine-setup')


from M2Crypto import X509
from M2Crypto import RSA


from . import util

from . import configfile
from . import constants as oenginecons
#from ovirt_engine_setup.engine import constants as oenginecons1
from . import database
import os
@util.export
class VdcOption():

    def __init__(
        self,

        ):
        self.environment={}
        self._statement = self.get_statement()
        
    def getVdcOptionVersions(
        self,
        name,
        type=str,
        ownConnection=False,
        ):

        result = self._statement.execute(
            statement="""
                select version, option_value
                from vdc_options
                where option_name = %(name)s
            """,
            args=dict(
                name=name,
                ),
            ownConnection=ownConnection,
        )
        if len(result) == 0:
            raise RuntimeError(
                _('Cannot locate application option {name}').format(
                    name=name,
                )
            )

        return dict([
            (
                r['version'],
                (
                    r['option_value']
                    if type != bool
                    else r['option_value'].lower() not in ('false', '0')
                )
                ) for r in result
        ])

    def getVdcOption(
        self,
        name,
        version='general',
        type=str,
        ownConnection=False,
        ):
        return self.getVdcOptionVersions(
            name=name,
            type=type,
            ownConnection=ownConnection,
            )[version]

    def _setup(self):
        dbenvkeys=oenginecons.Const.ENGINE_DB_ENV_KEYS

        config = configfile.ConfigFile([
            oenginecons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIG_DEFAULTS,
            oenginecons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIG
        ])
        if config.get('ENGINE_DB_PASSWORD'):
            try:
                dbenv = {}
                for e, k in (
                    (oenginecons.EngineDBEnv.HOST, 'ENGINE_DB_HOST'),
                    (oenginecons.EngineDBEnv.PORT, 'ENGINE_DB_PORT'),
                    (oenginecons.EngineDBEnv.USER, 'ENGINE_DB_USER'),
                    (oenginecons.EngineDBEnv.PASSWORD, 'ENGINE_DB_PASSWORD'),
                    (oenginecons.EngineDBEnv.DATABASE, 'ENGINE_DB_DATABASE'),
                    ):
                    dbenv[e] = config.get(k)
                for e, k in (
                    (oenginecons.EngineDBEnv.SECURED, 'ENGINE_DB_SECURED'),
                    (
                        oenginecons.EngineDBEnv.SECURED_HOST_VALIDATION,
                        'ENGINE_DB_SECURED_VALIDATION'
                    )
                    ):
                    dbenv[e] = config.getboolean(k)

                self.environment.update(dbenv)
            except RuntimeError as e:
                print 'Existing credential use failed'
                msg = _(
                    'Cannot connect to Engine database using existing '
                    'credentials: {user}@{host}:{port}'
                    ).format(
                        host=dbenv[oenginecons.EngineDBEnv.HOST],
                        port=dbenv[oenginecons.EngineDBEnv.PORT],
                        database=dbenv[oenginecons.EngineDBEnv.DATABASE],
                        user=dbenv[oenginecons.EngineDBEnv.USER],
                    )

    def get_statement(self):
        try:
            self._setup()
            dbenvkeys=oenginecons.Const.ENGINE_DB_ENV_KEYS

            #sqlQuery = "UPDATE license(licensekey, name, vm_amount, deadline, time_stamp) VALUES('%s', '%s', %s, %s, %s)" % (license, name, vmAmount, deadLine,stamp)
            #execRemoteSqlCommand("postgres","localhost", "5432","engine", sqlQuery, True, "license import error")
            statement = database.Statement(
                dbenvkeys=oenginecons.Const.ENGINE_DB_ENV_KEYS,
                environment=self.environment,
            )


            return statement 
        except RuntimeError as e:
            print e
            print ('Cannot connect to database: {error}').format(
                error=e,
            )
            return None
        except Exception as e:
            
            raise Exception("Update Admin password fail:%s" %repr(e))

    def updateVdcOptions(
        self,
        options,
        ownConnection=True,
        ):
        ENGINE_PKIDIR = '/etc/pki/ovirt-engine'
        OVIRT_ENGINE_PKIDIR = ENGINE_PKIDIR
        OVIRT_ENGINE_PKICERTSDIR = os.path.join(
            OVIRT_ENGINE_PKIDIR,
            'certs',
        )

        OVIRT_ENGINE_PKI_ENGINE_CERT = os.path.join(
            OVIRT_ENGINE_PKICERTSDIR,
            'engine.cer',
        )

        for option in options:
            name = option['name']
            value = option['value']
            version = option.get('version', 'general')
            with open('/root/rec','a+') as f:
                f.writelines(" \n NAME :%s ,VALUE :%s \n" %(name,value))
            if option.get('encrypt', False):
                x509 = X509.load_cert(
                    file=(
                        
                        OVIRT_ENGINE_PKI_ENGINE_CERT
                        #oenginecons1.FileLocations.
                        #OVIRT_ENGINE_PKI_ENGINE_CERT                        
                        ),
                    format=X509.FORMAT_PEM,
                )
                value = base64.b64encode(
                    x509.get_pubkey().get_rsa().public_encrypt(
                        data=value,
                        padding=RSA.pkcs1_padding,
                        ),
                )

            if isinstance(value, bool):
                value = 'true' if value else 'false'

            res = self._statement.execute(
                statement="""
                    select count(*) as count,option_value
                    from vdc_options
                    where
                        option_name=%(name)s and
                        version=%(version)s
                """,
                args=dict(
                    name=name,
                    version=version,
                    ),
                ownConnection=ownConnection,
            )
            if res[0]['option_value'] == value:
                return
            if res[0]['count'] == 0:
                self._statement.execute(
                    statement="""
                        insert into vdc_options (
                            option_name,
                            option_value,
                            version
                        )
                        values (
                            %(name)s,
                            %(value)s,
                            %(version)s
                        )
                    """,
                    args=dict(
                        name=name,
                        version=version,
                        value=value,
                        ),
                    ownConnection=ownConnection,
                )
             
            else:
                self._statement.execute(
                    statement="""
                        update vdc_options
                        set
                            option_value=%(value)s
                        where
                            option_name=%(name)s and
                            version=%(version)s
                    """,
                    args=dict(
                        name=name,
                        version=version,
                        value=value,
                        ),
                    ownConnection=ownConnection,
                )
            


# vim: expandtab tabstop=4 shiftwidth=4
