release note:
    针对ovirt-engine 的图形化配置界面

制作rpm包:
    配置文件为 源代码路径/setup.py,运行python setup.py bdist_rpm --force-arch=x86_64 即可.
    配置参数(以下是例子,详情清看源代码):
    在setup.py中的调用setup函数部分,看注释:
    setup(
        name = "ovirt_config", #软件包的名称，打包好的文件的名称。
        cmdclass={'build_py':build_py}, #编译类，是用distutils自带的编译类还是自定义的编译类，本程序是采用自定义的编译类。
        version="1.0",#版本号
        packages = ['ovirt/scripts','ovirt/Crrt/Crypto/Hash','ovirt/Crypto/Protocoovirtnode'],#需要安装的包
        data_files=[('/usr/bin', ['ovirt/node/setup/ovirt_config']), #数据文件，不需要编译，只需要安装的文件，在这里就是将
        #ovirt/node/setup/ovirt_config文件复制到/usr/bin目录下面

        )
    各种文件类型的打包方式步骤以及举例参考下面的依赖部分。
安装:
    有两种安装方式:
    RPM 包：
    1.ovirt_config：rpm -ivh ovirt_config-1.0-1.x86_64.rpm,ovirt_config界面 
    2.license_source:rpm -ivh licenseimport-1.0-1.x86_64.rpm,engie-setup的license plugin,针对之前的license plugin做了一点修改,
    也可以直接用这个，如果没有配置界面，将在命令行弹出一个对话框。
    源代码:python setup.py install
    

运行：
    运行ovirt_config命令

界面:
    界面包含以下几个部分:Status,Network,Local Storage,AD Operation,Add Hostname,Engine
    1.Status:
        显示当前的连接状态，网卡信息,有时不能检测到，例如/etc/sysconfig/network-scripts/ifcfg-*文件中如果没有配置type，则检测不了了.
    2.Network:
        配置hostname,和DNS，hostname是配置在内部的配置文件，ovirt_default.conf。key 是OVIRT_HOSTNAME，
        配置DNS和NTP
    3.Local Storage
        配置存储位置,在该位置创建一个目录，配置在内部配置文件:%{PYTHONLIB}/site-packages/ovirt/node/setup/ovirt_default.conf。
    4.AD Operation
        配置domain和port，配置在内部配置文件:%{PYTHONLIB}/site-packages/ovirt/node/setup/ovirt_default.conf
        ,key是OVIRT_COLLECTD_SERVER,OVIRT_COLLECTD_PORT.
    5.Add hostname
        配置/etc/hosts映射 
    6.配置ovirt-engine
        调用engine-setup --config=file 命令来完成配置工作，配置文件位于%{PYTHONLIB}/site-packages/ovirt/20141230183208-setup.conf
        配置文件可以从engine-setup配置结束后从:
        from ovirt_engine_setup import constants as osetupcons
        os.path.join(
             osetupcons.FileLocations.OVIRT_SETUP_ANSWERS_DIR,
             '%s-%s.conf' % (
                 datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                 self.environment[osetupcons.CoreEnv.ACTION],
             ),
         )
        这个路径读取到:在我本机上，这个路径是:/var/lib/ovirt-engine/setup/answers/ 目录，每次配置完后，engine-setup会自动生成一个文件用以记录配置项目:
        # action=setup
        [environment:default]
        OVESETUP_DIALOG/confirmSettings=none:None
        OVESETUP_CONFIG/applicationMode=str:both
        OVESETUP_CONFIG/remoteEngineSetupStyle=none:None
        OVESETUP_CONFIG/adminPassword=str:123
        OVESETUP_CONFIG/storageIsLocal=bool:False
        OVESETUP_CONFIG/firewallManager=none:None
        OVESETUP_CONFIG/remoteEngineHostRootPassword=none:None
        OVESETUP_CONFIG/updateFirewall=bool:False
        OVESETUP_CONFIG/remoteEngineHostSshPort=none:None
        OVESETUP_CONFIG/fqdn=str:localhost.localdomain
        OVESETUP_CONFIG/storageType=none:None
        OSETUP_RPMDISTRO/requireRollback=none:None
        OSETUP_RPMDISTRO/enableUpgrade=none:None
        OVESETUP_DB/database=str:engine
        OVESETUP_DB/fixDbViolations=none:None
        OVESETUP_DB/secured=bool:False
        OVESETUP_DB/host=str:localhost
        OVESETUP_DB/user=str:engine
        OVESETUP_DB/securedHostValidation=bool:False
        OVESETUP_DB/port=int:5432
        OVESETUP_ENGINE_CORE/enable=bool:True
        OVESETUP_CORE/engineStop=none:None
        OVESETUP_SYSTEM/memCheckEnabled=bool:True
        OVESETUP_SYSTEM/nfsConfigEnabled=bool:True
        OVESETUP_PKI/organization=str:localdomain
        OVESETUP_CONFIG/isoDomainMountPoint=str:/var/lib/exports/iso
        OVESETUP_CONFIG/isoDomainName=str:ISO_DOMAIN
        OVESETUP_CONFIG/isoDomainACL=str:localhost.localdomain(rw)
        OVESETUP_AIO/configure=none:None
        OVESETUP_AIO/storageDomainName=none:None
        OVESETUP_AIO/storageDomainDir=none:None
        OVESETUP_PROVISIONING/postgresProvisioningEnabled=bool:True
        OVESETUP_APACHE/configureRootRedirection=bool:True
        OVESETUP_APACHE/configureSsl=bool:False
        OVESETUP_CONFIG/websocketProxyConfig=bool:False

        
依赖:
    当你遇到一个依赖问题时，通常情况下，程序会直接给出提示,例如:No Module named ****，因此，这个程序开始从0.75上面拷过来的时候，依赖是作为第三方包独立安装的，
    在这里，所有的第三方包(依赖)都被打包进入到这个安装文件中。当你需要打包一个依赖的时候，你需要根据依赖的后缀来修改setup.py文件。
    这里我例举几个例子来说明:
    1.so文件:
        此文件不需要在程序编译过程中重新编译，所以，只需要copy到安装目录即可
        步骤:
        1.在setup.py的自定义编译类build_py的find_package_modules函数中,找到module_files = glob(os.path.join(package_dir, "*.py")) ,根据这个格式
         添加so_module_file=glob(os.path.join(package_dir, "*.so")) ,意思除了在源代码目录中找py文件还必须找so文件。
        2.在自定义编译类中get_module_outfile函数中，加上
            if os.path.splitext(module_file)[1] =='.so':
                outfile_path = [build_dir] + list(package) + [module + ".so"]
                return os.path.join(*outfile_path)
         表示该so文件复制的到安装目录的路径和名称，这个是保留原有名称。
    2.py文件
        单一以py文件作为依赖的模块有:augeas.py和pam.py,这里它们将直接安装到python 的site-packages目录下，
        步骤:
        1.在setup.py中调用setup函数部分添加py_modules参数，类型是list,例如：
            py_modules=['pam','augeas']，路径为和当前setup.py文件相对的路径。这里是和setup.py同级。
            

    3.python package:
        步骤:
        1.在setup.py中的setup函数调用中添加packages参数，类型为list,例如:
         packages = ['ovirt/scripts','ovirt/Crypto/Util']，路径为相对与setup.py的路径。
    4.普通文件:
        普通文件是指不需要在打包过程中编译的文件，并且，安装路径可以是目标系统的任意路径。跟so文件相比是so文件必须放在一个指定的路径下，不然程序就会import失败，
        步骤:
        1.在setup.py文件的setup调用中添加data_files参数，类型为list,例如:
        data_files=[('/usr/bin', ['ovirt/node/setup/ovirt_config']),]
        
程序细节:
    这里列出跟0.75上代码相比所作的变化，因为我是根据0.75上的代码来改的。插件位置统一放在ovirt/node/setup/文件夹下。
    1.运行流程:
        1.用户运行ovirt_config命令;
        2.选择Engine项目;
        3.填写Engine配置表单;
        4.用户单击save&engine-setup保存配置选项;
        5.调用engine_page.py中on_merge函数，保存配置选项到engine_config,即调用EngineConfig的update方法，这个方法上面已说已经重载了;
        6.调转到setup插件,调用setup插件中的on_merge函数;
        7.调用engine-setup --config=file 命令
        8.调用self._miscEncrypted()函数,判断管理员密码是否有变化，如果有修改管理员密码
        9.copy engine-setup自动生成的配置文件覆盖原配置文件.
    2.更改细节
        1.engine_page.py(在ovirt/node/setup/engine_page.py中)，因为和0.75上已经安装的ovirt-engine版本不一样，因此，调用的过程也略有不一样：
            主要更改有：
            1.EngineConfig类(在ovirt/node/setup/engine_page.py中):
                1.重载了retrieve方法.
                2.在基类NodeConfigFileSection类中添加_map_and_update_defaults_decorator装饰体
            2.新添加EngineCfgProvider类:
                1.重载__init__函数
                2.重载get_dict函数
                3.重载_write函数
                4.重载update函数
                5.添加_readEnvironment函数
            3.修改plugin类的__init__方法
                1.添加自定义配置文件的路径逻辑,这里是把配置路径放在ovirt文件夹下面，20141230183208-setup.conf
                2.调用ConfigFile的时，把自定义的provider，就是上面的EngineCfgProvider作为第二个参数。以使用自定义的配置解析逻辑。
                
            4.model函数
                这个函数主要的修改是改变cfg变量的key名称，因为和75上不使用同一个配置文件，因此，配置文件的key不一样。
                
            5.on_merge函数
                调用我们上面的EngineConfig类实例方法有些不同，因为有些函数重载了
                1.EngineConfig().update函数
                    1.参数的传递方式,由原来的位置参数改为key参数，
                    2.参数的key就是配置文件中的key,保持一致。
                2.EngineConfig()._advance_configure函数
                    1.参数的传递方式,由原来的位置参数改为key参数;
                    2.参数的key就是配置文件中的key,保持一致;
                    3.判断firewall是否已经配置,例子:
                        if firewall:
                            piece.update({"OVESETUP_CONFIG/updateFirewall":True,"OVESETUP_CONFIG/firewallManager":firewall})
                        elif firewall== False:
                            piece.update({"OVESETUP_CONFIG/updateFirewall":False,"OVESETUP_CONFIG/firewallManager":None})
        2.setup.py(在ovirt/node/setup/setup.py中)
            主要的更改 :
            1.添加_miscEncrypted函数:
                该函数用来处理自定义的管理员界面登陆密码，就是admin用户的密码
            2.on_merge函数:
                1.修改cmd变量为：
                    cmd = "engine-setup --config="+self.filename，
                    因为新版本的engine-setup命令调用略有不同。
                2.修改配置完成提示语:
                    self.widgets["ping.result"].text('')
                    self.widgets["ping.result"].text("Operate successfully")