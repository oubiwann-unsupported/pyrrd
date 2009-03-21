class XMLNode(object):
    """
    """
    def __init__(self, tree, attribute_names):
        self.tree = tree
        self.attributes = {}
        for name, cast, default in attribute_names:
            try:
                value = cast(self.getAttribute(name))
            except ValueError:
                value = default
            if not value:
                value = default
            self.attributes[name] = value
        

    def getAttribute(self, attrName):
        """
        """
        ### BUGFIX - Handle failure to find the node. @ AW
        node = self.tree.find(attrName)
        if node!=None:
          return node.text.strip()
        raise ValueError()
        ### END BUGFIX


class DSXMLNode(XMLNode):
    """
    """


class CDPPrepXMLNode(XMLNode):
    """
    """
    def __init__(self, tree):
        self.ds = []
        dsAttributes = [
            ("primary_value", float, 0.0),
            ("secondary_value", float, 0.0),
            ("value", float, 0.0),
            ("unknown_datapoints", int, 0),
            ]
        for ds in tree.findall("ds"):
            self.ds.append(DSXMLNode(ds, dsAttributes))


class RRAXMLNode(XMLNode):
    """
    """
    def __init__(self, tree, attributes, include_data=False):
        super(RRAXMLNode, self).__init__(tree, attributes)
        self.database = None
        ### BUGFIX - There might not be an xff element for Holt-Winters
        ### RRAs. @AW
        xff = self.tree.find('params').find('xff')
        if xff!=None:
          xff = float(xff.text)
          self.attributes["xff"] = xff
        ### END BUGFIX

        self.cdp_prep = CDPPrepXMLNode(self.tree.find("cdp_prep"))
        if include_data:
            db = self.tree.get("database")
            self.database = DatabaseNode(db)


class RRDXMLNode(XMLNode):
    """
    """
    def __init__(self, tree, include_data=False):
        attributes = [
            ("version", int, 0),
            ("step", int, 300),
            ("lastupdate", int, 0),
            ]
        super(RRDXMLNode, self).__init__(tree, attributes)
        dsAttributes = [
            ("name", str, ""),
            ("type", str, "GAUGE"),
            ("minimal_heartbeat", int, 300),
            ("min", int, "NaN"),
            ("max", int, "NaN"),
            ("last_ds", int, 0),
            ("value", float, 0.0),
            ("unknown_sec", int, 0),
            ]
        rraAttributes = [
            ("cf", str, "AVERAGE"),
            ("pdp_per_row", int, 0),
            ]
        self.ds = []
        self.rra = []
        for ds in self.getDataSources():
            self.ds.append(DSXMLNode(ds, dsAttributes))
        for rra in self.getRRAs():
            self.rra.append(RRAXMLNode(rra, rraAttributes, include_data))

    def getDataSources(self):
        """
        """
        return self.tree.findall("ds")

    def getRRAs(self):
        """
        """
        return self.tree.findall("rra")
