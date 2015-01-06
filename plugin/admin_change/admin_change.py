#from ovirt.node.utils import vdcoption


import gettext
_ = lambda m: gettext.dgettext(message=m, domain='ovirt-engine-setup')


from otopi import constants as otopicons
from otopi import util
from otopi import plugin


from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common \
    import constants as oengcommcons
from ovirt_engine_setup import dialog
from ovirt_engine_setup.engine import vdcoption

class Plugin(plugin.PluginBase):
    
    def __init__(self, context):
        super(Plugin, self).__init__(context=context)
        self._enabled = True


        
        
        
    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        
        priority=plugin.Stages.PRIORITY_LAST+20,
        condition=lambda self: self._enabled,
    )
    def _miscEncrypted_custom(self):
        if not self.environment.get('TUI_change_admin',False):
            return
        vdcoption.VdcOption(
            statement=self.environment[
                oenginecons.EngineDBEnv.STATEMENT
            ]
        ).updateVdcOptions(
            options=(
                {
                    'name': 'LocalAdminPassword',
                    'value': self.environment[
                        osetupcons.ConfigEnv.ADMIN_PASSWORD
                    ],
                    'encrypt': True,
                },
                {
                    'name': 'AdminPassword',
                    'value': self.environment[
                        osetupcons.ConfigEnv.ADMIN_PASSWORD
                    ],
                    'encrypt': True,
                },
            ),
        )


    def __miscEncrypted(self):
        import ovirt.node.utils.vdcoption as vdcoption
        vdcoption.VdcOption().updateVdcOptions(
            options=(
                {
                    'name': 'LocalAdminPassword',
                    'value': self.environment[
                        'OVESETUP_CONFIG/adminPassword'
                        ],
                    'encrypt': True,
                    },
                {
                    'name': 'AdminPassword',
                    'value': self.environment[
                        'OVESETUP_CONFIG/adminPassword'
                        ],
                    'encrypt': True,
                    },
                ),
        )    
