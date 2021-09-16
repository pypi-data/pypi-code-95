import logging
from git import Repo
from chibi.file import Chibi_path
from chibi_command import Command


logger = logging.getLogger( 'chibi_command.git' )


class Git:
    @classmethod
    def repo( cls, src ):
        if src is None:
            src = Chibi_path.current_dir()
        return Repo( src )

    @classmethod
    def clone( cls, url, dest=None ):
        """
        clona el repositorio de la url

        Parameters
        ==========
        url: string
            url del repositorio
        dest: string ( optional )
            destino de donde se clonara el repositorio
            por default es el directorio de trabajo
        """
        if dest is None:
            dest = Chibi_path.current_dir()
        Repo.clone_from( url, str( dest ) )

    @classmethod
    def pull( cls, src=None ):
        """
        hace pull a un repositorio

        Parameters
        ==========
        src: string
            ruta del repositorio que se quiere hacer pull
        """
        repo = cls.repo( src )
        repo.remote().pull()

    @classmethod
    def checkout( cls, branch, src=None ):
        repo = cls.repo( src )
        current_branch = repo.active_branch
        logger.info( f"cambiando '{current_branch.name}' a '{branch}'" )
        repo.git.checkout( branch )
