import abc
import logging
from contextlib import contextmanager

import pydicom
from pynetdicom import AE
from pynetdicom.presentation import build_context

from pacs_config import PacsConfiguration

STATUS_SUCCESS = 0x0000


class PacsError(Exception):
    pass


class AbstractPacsClient(abc.ABC):

    @abc.abstractmethod
    def store_dicom_dataset(self, dataset: pydicom.Dataset):
        raise NotImplementedError


class PacsClient(AbstractPacsClient):

    def __init__(self, config: PacsConfiguration):
        self.ae_title = config.ae_title
        self.host = config.host
        self.port = config.port
        self.dimse_timeout = config.dimse_timeout

    @contextmanager
    def _association(self, dataset):
        self.ae = AE(self.ae_title)
        self.ae.requested_contexts = [build_context(dataset.SOPClassUID,
                                                    dataset.file_meta.TransferSyntaxUID)]
        assoc = self.ae.associate(self.host, self.port)
        assoc.dimse_timeout = self.dimse_timeout
        yield assoc
        assoc.release()

    def store_dicom_dataset(self, dataset: pydicom.Dataset):
        try:
            with self._association(dataset) as assoc:
                if assoc.is_established:
                    status = assoc.send_c_store(dataset)
                    if getattr(status, 'Status', None) == STATUS_SUCCESS:
                        logging.info("Saved dicom to Pacs")
                    else:
                        raise PacsError()
                else:
                    raise PacsError("Association not established")
        except Exception as e:
            logging.exception("Failed saving dicom to Pacs")
            if isinstance(e, PacsError):
                raise
            else:
                raise PacsError(repr(e))
