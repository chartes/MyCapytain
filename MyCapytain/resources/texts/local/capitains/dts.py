# -*- coding: utf-8 -*-
"""


"""
from MyCapytain.common.constants import XPATH_NAMESPACES
from MyCapytain.common.reference import Citation, URN as URNCTS, CtsReference
from MyCapytain.errors import MissingRefsDecl
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText, CapitainsCtsPassage

__all__ = [
    "CapitainsDtsText",
    "CapitainsDtsPassage"
]


class URNDTS(URNCTS):

    def __parse__(self, urn):
        """ Parse a URN

        :param urn: A URN:CTS
        :type urn: basestring
        :rtype: defaultdict.basestring
        :returns: Dictionary representation
        """
        parsed = URNCTS.model()
        self.__urn = urn.split("#")[0]
        urn = self.__urn.split(":")
        if isinstance(urn, list) and len(urn) > 2:
            parsed["urn_namespace"] = urn[1]
            parsed["cts_namespace"] = urn[2]

            if len(urn) == 5:
                parsed["reference"] = DtsReference(urn[4])

            if len(urn) >= 4:
                urn = urn[3].split(".")
                if len(urn) >= 1:
                    parsed["textgroup"] = urn[0]
                if len(urn) >= 2:
                    parsed["work"] = urn[1]
                if len(urn) >= 3:
                    parsed["version"] = urn[2]
        else:
            raise ValueError("URN is empty and I'm so sad about it")
        return parsed


class CapitainsDtsText(CapitainsCtsText):

    def __init__(self, urn=None, citation=None, resource=None):
        u = URNDTS(str(urn))
        super(CapitainsDtsText, self).__init__(urn=u, citation=citation, resource=resource)

    def _findCRefPattern(self, xml):
        """ Find CRefPattern in the text and set object.citation
        :param xml: Xml Resource
        :type xml: lxml.etree._Element
        :return: None
        """
        if not self.citation.is_set():
            citation = xml.xpath("//tei:refsDecl[@n='capitains']", namespaces=XPATH_NAMESPACES)
            if len(citation):
                self.citation = Citation.ingest(resource=citation[0], xpath=".//tei:cRefPattern")
            else:
                raise MissingRefsDecl("No reference declaration (refsDecl) found.")

CapitainsDtsPassage = CapitainsCtsPassage
