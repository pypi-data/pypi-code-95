from setux.core.distro import Distro


class Debian(Distro):
    Package = 'apt'
    Service = 'SystemD'
    pkgmap = dict(
        pip        = 'python3-pip',
        setuptools = 'python3-setuptools',
        sqlite     = 'sqlite3',
        p7zip      = 'p7zip-full',
        xz         = 'xz-utils',
        ctag       = 'exuberant-ctags',
        unrar      = 'unrar-free',
        gvim       = 'vim-gtk3',
    )
    svcmap = dict(
    )

    @classmethod
    def release_name(cls, infos):
        did = infos['ID'].strip().capilalize()
        ver = infos['VERSION_ID'].strip('\r"')
        return f'{did}_{ver}'


class Debian_9(Debian):
    ''' Stretch '''


class Debian_10(Debian):
    ''' Buster '''


class Debian_11(Debian):
    ''' Bullseye '''

