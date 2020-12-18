# -*- coding: utf-8 -*-
"""


"""
import lxml.etree as etree

from typing import Tuple, Optional
from MyCapytain.common.constants import XPATH_NAMESPACES
from MyCapytain.resources.prototypes.text import InteractiveTextualNode
from MyCapytain.resources.texts.base.tei import TeiResource
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsPassage, CtsReference, CtsReferenceSet
#A voir si on garde ou si on doit modifier
from MyCapytain.common.reference import Citation
from MyCapytain.resources.prototypes.cts.text import PrototypeCtsPassage, PrototypeCtsText

__all__ = [
    "CapitainsDtsText",
    "CapitainsDtsPassage"
]

CapitainsDtsPassage = CapitainsCtsPassage

#TODO
# forker DtsCitation et DtsCitationSet

#TODO
class _NewSharedMethods(TeiResource):
    def getTextualNode(self, textId=None, subreference=None, simple=False):
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
            identifier=identifier,
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
                identifier=self.identifier,
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
            identifier=self.identifier,
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

class _SimplePassage(_NewSharedMethods, PrototypeCtsPassage):
    """ CapitainsCtsPassage for simple and quick parsing of texts

    :param resource: Element representing the passage
    :type resource: etree._Element
    :param reference: CapitainsCtsPassage reference
    :type reference: CtsReference
    :param urn: URN of the source text or of the passage
    :type urn: URN
    :param citation: XmlCtsCitation scheme of the text
    :type citation: Citation
    :param text: CtsTextMetadata containing the passage
    :type text: CapitainsCtsText
    """
    def __init__(self, resource, reference, citation, text, identifier=None):
        super(_SimplePassage, self).__init__(
            resource=resource,
            citation=citation,
            **_make_passage_kwargs(identifier, reference)
        )
        self._text = text
        self._reference = reference
        self._children = None
        self._depth = 0
        if reference is not None:
            self._depth = reference.depth
        self._prev_next = None

    @property
    def reference(self):
        """ URN CapitainsCtsPassage CtsReference

        :return: CtsReference
        :rtype: CtsReference
        """
        return self._reference

    @reference.setter
    def reference(self, value):
        self._reference = value

    @property
    def childIds(self):
        """ Children of the passage

        :rtype: None, CtsReference
        :returns: Dictionary of chidren, where key are subreferences
        """
        if self.depth >= len(self.citation.root):
            return []
        elif self._children is not None:
            return self._children
        else:
            self._children = self.getReffs()
            return self._children

    def getReffs(self, level=1, subreference=None) -> CtsReferenceSet:
        """ Reference available at a given level

        :param level: Depth required. If not set, should retrieve first encountered level (1 based). 0 retrieves inside
            a range
        :param subreference: Subreference (optional)
        :returns: List of levels
        """
        level += self.depth
        if not subreference:
            subreference = self.reference
        return self.textObject.getValidReff(level, reference=subreference)

    def getTextualNode(self, subreference: CtsReference=None):
        """ Special GetPassage implementation for SimplePassage (Simple is True by default)

        :param subreference:
        :return:
        """
        if not isinstance(subreference, CtsReference):
            subreference = CtsReference(subreference)
        return self.textObject.getTextualNode(subreference)

    @property
    def nextId(self):
        """ Next passage

        :returns: Next passage at same level
        :rtype: None, CtsReference
        """
        return self.siblingsId[1]

    @property
    def prevId(self) -> Optional[CtsReference]:
        """ Get the Previous passage reference

        :returns: Previous passage reference at the same level
        :rtype: None, CtsReference
        """
        return self.siblingsId[0]

    @property
    def siblingsId(self) -> Tuple[CtsReference, CtsReference]:
        """ Siblings Identifiers of the passage

        :rtype: (str, str)
        """

        if not self._text:
            raise MissingAttribute("CapitainsCtsPassage was iniated without CtsTextMetadata object")
        if self._prev_next is not None:
            return self._prev_next

        document_references = self._text.getReffs(level=self.depth)

        range_length = 1
        if self.reference.is_range():
            range_length = len(self.getReffs())

        start = document_references.index(self.reference.start)

        if start == 0:
            # If the passage is already at the beginning
            _prev = None
        elif start - range_length < 0:
            _prev = document_references[0]
        else:
            _prev = document_references[start - 1]

        if start + 1 == len(document_references):
            # If the passage is already at the end
            _next = None
        elif start + range_length > len(document_references):
            _next = document_references[-1]
        else:
            _next = document_references[start + 1]

        self._prev_next = (_prev, _next)
        return self._prev_next

    @property
    def textObject(self):
        """ CtsTextMetadata Object. Required for NextPrev

        :rtype: CapitainsCtsText
        """
        return self._text

#TODO
class CapitainsDtsText(_NewSharedMethods):
    def __init__(self, identifier=None, citation=None, resource=None):
        super(CapitainsDtsText, self).__init__(identifier=identifier, citation=citation, resource=resource)

        if self.resource is not None:
            self._findCRefPattern(self.resource)

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

    def test(self):
        """ Parse the object and generate the children
        """
        try:
            xml = self.xml.xpath(self.citation.scope, namespaces=XPATH_NAMESPACES)
            if len(xml) == 0:
                msg = "Main citation scope does not result in any result ({0})".format(self.citation.scope)
                raise RefsDeclError(msg)
        except Exception as E:
            raise E

