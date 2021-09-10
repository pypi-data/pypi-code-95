from setux.core.distro import Distro


class FreeBSD(Distro):
    Package = 'pkg'
    Service = 'Service'
    pkgmap = dict(
        pip        = 'py37-pip',
        setuptools = 'py37-setuptools',
        sshfs      = 'fusefs-sshfs',
        xz         = 'xzip',
        shellcheck = 'hs-ShellCheck',
    )
    svcmap = dict(
        ssh = 'sshd',
    )

    @classmethod
    def release_infos(cls, target):
        ret, out, err = target.run('uname -s', report='quiet')
        distro = out[0]
        if distro=='FreeBSD':
            ret, out, err = target.run('uname -r', report='quiet')
            ver = out[0].split('.')[0]
            return dict(
                ID         = distro,
                VERSION_ID = ver,
            )


class FreeBSD_12(FreeBSD): pass


class FreeBSD_13(FreeBSD): pass

