from confz import ConfZ

class ZenohConfig(ConfZ):
    mode: str = 'peer'
    connect: str = None
    listen: str = None
    config: str = None

