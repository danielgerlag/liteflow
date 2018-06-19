import logging
from interface import implements
import threading
from azure.storage.blob import BlockBlobService, PublicAccess
from azure.common import AzureException
from azure.storage.common import CloudStorageAccount
from liteflow.core.abstractions import ILockProvider


class AzureLockProvider(implements(ILockProvider)):

    container_name = 'liteflow-locks'

    def __init__(self, account: CloudStorageAccount):
        self._logger = logging.getLogger(str(self.__class__))
        self._leases = {}
        self._service = account.create_block_blob_service()
        self._service.create_container(self.container_name, public_access=PublicAccess.Blob)
        self._lock = threading.Lock()
        self._renew_timer = threading.Timer(30, self.renew_leases)
        self._renew_timer.start()

    def acquire_lock(self, resource) -> bool:
        try:
            if not self._service.exists(self.container_name, resource):
                self._service.create_blob_from_text(self.container_name, resource, '')
            lease_id = self._service.acquire_blob_lease(self.container_name, resource, lease_duration=60)
            self._leases[resource] = lease_id
            self._logger.log(logging.DEBUG, f"Acquired lock for {resource} with lease {lease_id}")
            return True
        except Exception as ex:
            self._logger.log(logging.DEBUG, f"Failed to acquire lock for {resource} - {ex}")
            return False

    def release_lock(self, resource):
        try:
            self._lock.acquire()
            if resource in self._leases:
                self._service.release_blob_lease(self.container_name, resource, self._leases[resource])
                del self._leases[resource]
        except Exception as ex:
            self._logger.log(logging.ERROR, f"Failed to release lock - {ex}")
        finally:
            self._lock.release()

    def shutdown(self):
        self._renew_timer.cancel()

    def renew_leases(self):
        self._logger.log(logging.INFO, "Renewing active azure blob storage leases")
        try:
            for resource in self._leases:
                self._service.renew_blob_lease(self.container_name, resource, self._leases[resource])
        except Exception as ex:
            self._logger.log(logging.ERROR, f"Error renewing leases - {ex}")
        finally:
            self._renew_timer = threading.Timer(30, self.renew_leases)
            self._renew_timer.start()
