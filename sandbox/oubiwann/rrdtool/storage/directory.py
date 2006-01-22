
class DirectoryStorage:

    def __init__(self, base_dir):
        self.base_dir = base_dir

        self.service_base = '%s/service_' % base_dir
        self.service_src = '%s_%s_src.rrd' % (self.service_base, '%s')
        self.service_dst = '%s_%s_dst.rrd' % (self.service_base, '%s')

        self.proto_base = '%s/protocol_' % base_dir
        self.proto_src = '%s_%s_src.rrd' % (self.proto_base, '%s')
        self.proto_dst = '%s_%s_dst.rrd' % (self.proto_base, '%s')

        

    def getRouterList(self):
        pass   

    def getRouters(self):
        pass

    def getNetworkList(self):
        pass

    def getNetworks(self):
        pass

    def getProtocolList(self):
        pass

    def getProtocols(self):
        pass

    def getServiceList(self):
        pass

    def getServices(self):
        pass

    def getTOSList(self):
        pass

    def getTOS(self):
        pass

    def getASList(self):
        pass

    def getASs(self):
        pass

