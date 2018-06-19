from interface import Interface


class IBackgroundService(Interface):

    def start(self):
        pass

    def stop(self):
        pass