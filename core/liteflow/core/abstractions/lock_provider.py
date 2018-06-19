from interface import Interface


class ILockProvider(Interface):

    def acquire_lock(self, resource) -> bool:
        pass

    def release_lock(self, resource):
        pass

    def shutdown(self):
        pass