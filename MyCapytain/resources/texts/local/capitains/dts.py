# -*- coding: utf-8 -*-
"""


"""
import lxml.etree as etree

from MyCapytain.resources.prototypes.text import InteractiveTextualNode
from MyCapytain.resources.texts.base.tei import TeiResource
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsPassage

__all__ = [
    "CapitainsDtsText",
    "CapitainsDtsPassage"
]

CapitainsDtsPassage = CapitainsCtsPassage

#TODO
# forker DtsCitation et DtsCitationSet

#TODO
class _NewSharedMethods(TeiResource):
    def getTextualNode(self, subreference=None, simple=False):
        """ Finds a passage in the current text

        :param subreference: Identifier of the subreference / passages
        :type subreference: Union[list, CtsReference]
        :param simple: If set to true, retrieves nodes up to the given one, cleaning non required siblings.
        :type simple: boolean
        :rtype: CapitainsCtsPassage, ContextPassage
        :returns: Asked passage
        """
        if subreference is None:
            return self._getSimplePassage()

        if not isinstance(subreference, CtsReference):
            if isinstance(subreference, str):
                subreference = CtsReference(subreference)
            elif isinstance(subreference, list):
                subreference = CtsReference(".".join(subreference))

        if len(subreference.start) > self.citation.root.depth:
            raise CitationDepthError("URN is deeper than citation scheme")

        if simple is True:
            return self._getSimplePassage(subreference)

        if not subreference.is_range():
            start = end = subreference.start.list
        else:
            start, end = subreference.start.list, subreference.end.list

        citation_start = self.citation.root[len(start) - 1]
        citation_end = self.citation.root[len(end) - 1]

        start, end = citation_start.fill(passage=start), citation_end.fill(passage=end)
        start, end = normalizeXpath(start.split("/")[2:]), normalizeXpath(end.split("/")[2:])

        xml = self.textObject.xml

        if isinstance(xml, etree._Element):
            root = copyNode(xml)
        else:
            root = copyNode(xml.getroot())

        root = passageLoop(xml, root, start, end)

        if self.urn:
            urn = URN("{}:{}".format(self.urn, subreference))
        else:
            urn = None

        return CapitainsCtsPassage(
            urn=urn,
            resource=root,
            text=self,
            citation=citation_start,
            reference=subreference
        )

    def _getSimplePassage(self, reference=None):
        """ Retrieve a single node representing the passage.

        .. warning:: Range support is awkward.

        :param reference: Identifier of the subreference / passages
        :type reference: list, reference
        :returns: Asked passage
        :rtype: CapitainsCtsPassage
        """
        if reference is None:
            return _SimplePassage(
                resource=self.resource,
                reference=None,
                urn=self.urn,
                citation=self.citation.root,
                text=self
            )

        subcitation = self.citation.root[reference.depth - 1]
        resource = self.resource.xpath(
            subcitation.fill(reference),
            namespaces=XPATH_NAMESPACES
        )

        if len(resource) != 1:
            raise InvalidURN

        return _SimplePassage(
            resource[0],
            reference=reference,
            urn=self.urn,
            citation=subcitation,
            text=self.textObject
        )

    @property
    def textObject(self):
        """ Textual Object with full capacities (Unlike Simple CapitainsCtsPassage)

        :rtype: CtsTextMetadata, CapitainsCtsPassage
        :return: Textual Object with full capacities (Unlike Simple CapitainsCtsPassage)
        """
        text = None
        if isinstance(self, CapitainsCtsText):
            text = self
        return text

    def getReffs(self, level: int = 1, subreference: CtsReference = None) -> CtsReferenceSet:
        """ CtsReference available at a given level

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :param subreference: Subreference (optional)
        :returns: List of levels
        """

        if not subreference and hasattr(self, "reference"):
            subreference = self.reference
        elif subreference and not isinstance(subreference, CtsReference):
            subreference = CtsReference(subreference)

        return self.getValidReff(level=level, reference=subreference)


    def xpath(self, *args, **kwargs):
        """ Perform XPath on the passage XML

        :param args: Ordered arguments for etree._Element().xpath()
        :param kwargs: Named arguments
        :return: Result list
        :rtype: list(etree._Element)
        """
        if "smart_strings" not in kwargs:
            kwargs["smart_strings"] = False
        return self.resource.xpath(*args, **kwargs)

    def tostring(self, *args, **kwargs):
        """ Transform the CapitainsCtsPassage in XML string

        :param args: Ordered arguments for etree.tostring() (except the first one)
        :param kwargs: Named arguments
        :return:
        """
        return etree.tostring(self.resource, *args, **kwargs)

#TODO
class CapitainsDtsText(InteractiveTextualNode, _NewSharedMethods):
    pass

