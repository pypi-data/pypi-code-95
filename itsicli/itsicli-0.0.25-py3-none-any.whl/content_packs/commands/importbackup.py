# ${copyright}

import os

from pathlib import Path

from itsicli.setup_logging import logger
from itsicli.content_packs.backup.workspace_import import BackupImporter
from itsicli.content_packs.commands.base import WorkspaceCommand


class ImportBackupCommand(WorkspaceCommand):

    HELP = 'import the content in a backup file'

    NAME = 'importbackup'

    class Args(object):
        BACKUP_FILE_PATH = 'backup_file_path'

    @classmethod
    def add_to_parser(cls, parser):
        subparser = parser.add_parser(cls.NAME, help=cls.HELP)
        subparser.add_argument('{}'.format(cls.Args.BACKUP_FILE_PATH), help='the ITSI backup file path')
        return subparser

    def run(self, args):
        backup_file = getattr(args, self.Args.BACKUP_FILE_PATH)

        logger.info("Backup file path is set to '{}'".format(backup_file))

        self.import_from_backup_file(self.config.id, backup_file)

        logger.info('Done.')

    def import_from_backup_file(self, content_pack_id, backup_file):
        if not backup_file:
            return

        backup_path = Path(os.path.expanduser(backup_file)).resolve()

        importer = BackupImporter(content_pack_id)
        importer.import_backup(backup_path)
