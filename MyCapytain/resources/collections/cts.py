# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml
   :synopsis: XML based CtsTextMetadata and repository

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals

from rdflib import URIRef, Literal
from rdflib.namespace import XSD
from lxml.objectify import IntElement, FloatElement

from MyCapytain.resources.prototypes.cts import inventory as cts
from MyCapytain.common.reference._capitains_cts import Citation as CitationPrototype
from MyCapytain.common.utils import xmlparser, expand_namespace
from MyCapytain.common.constants import XPATH_NAMESPACES, Mimetypes, RDF_NAMESPACES


_CLASSES_DICT = {}


class XmlCtsCitation(CitationPrototype):
    """ XmlCtsCitation XML implementation for CtsTextInventoryMetadata

    """

    @staticmethod
    def ingest(resource, element=None, xpath="ti:citation", _cls_dict=_CLASSES_DICT):
        """ Ingest xml to create a citation

        :param resource: XML on which to do xpath
        :param element: Element where the citation should be stored
        :param xpath: XPath to use to retrieve citation

        :return: XmlCtsCitation
        """
        # Reuse of of find citation
        results = resource.xpath(xpath, namespaces=XPATH_NAMESPACES)
        CLASS = _cls_dict.get("citation", XmlCtsCitation)
        if len(results) > 0:
            citation = CLASS(
                name=results[0].get("label"),
                xpath=results[0].get("xpath"),
                scope=results[0].get("scope")
            )

            if isinstance(element, CLASS):
                element.child = citation
                CLASS.ingest(
                    resource=results[0],
                    element=element.child
                )
            else:
                element = citation
                CLASS.ingest(
                    resource=results[0],
                    element=element
                )

            return citation

        return None


def xpathDict(xml, xpath, cls, parent, **kwargs):
    """ Returns a default Dict given certain information

    :param xml: An xml tree
    :type xml: etree
    :param xpath: XPath to find children
    :type xpath: str
    :param cls: Class identifying children
    :type cls: inventory.Resource
    :param parent: Parent of object
    :type parent: CtsCollection
    :rtype: collections.defaultdict.<basestring, inventory.Resource>
    :returns: Dictionary of children
    """
    children = []
    for child in xml.xpath(xpath, namespaces=XPATH_NAMESPACES):
        children.append(cls.parse(
            resource=child,
            parent=parent,
            **kwargs
        ))
    return children


def __parse_structured_metadata__(obj, xml):
    """ Parse an XML object for structured metadata

    :param obj: Object whose metadata are parsed
    :param xml: XML that needs to be parsed
    """
    for metadata in xml.xpath("cpt:structured-metadata/*", namespaces=XPATH_NAMESPACES):
        tag = metadata.tag
        if "{" in tag:
            ns, tag = tuple(tag.split("}"))
            tag = URIRef(ns[1:]+tag)
            s_m = str(metadata)
            if s_m.startswith("urn:") or s_m.startswith("http:") or s_m.startswith("https:") or s_m.startswith("hdl:"):
                obj.metadata.add(
                    tag,
                    URIRef(metadata)
                )
            elif '{http://www.w3.org/XML/1998/namespace}lang' in metadata.attrib:
                obj.metadata.add(
                    tag,
                    s_m,
                    lang=metadata.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                )
            else:
                if "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype" in metadata.attrib:
                    datatype = metadata.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype"]
                    if not datatype.startswith("http") and ":" in datatype:
                        datatype = expand_namespace(metadata.nsmap, datatype)
                    obj.metadata.add(tag, Literal(s_m, datatype=URIRef(datatype)))
                elif isinstance(metadata, IntElement):
                    obj.metadata.add(tag, Literal(int(metadata), datatype=XSD.integer))
                elif isinstance(metadata, FloatElement):
                    obj.metadata.add(tag, Literal(float(metadata), datatype=XSD.float))
                else:
                    obj.metadata.add(tag, s_m)


class XmlCtsTextMetadata(cts.CtsTextMetadata):
    """ Represents a CTS CtsTextMetadata

    """
    DEFAULT_EXPORT = Mimetypes.PYTHON.ETREE

    @staticmethod
    def __findCitations(obj, xml, xpath="ti:citation"):
        """ Find citation in current xml. Used as a loop for xmlparser()

        :param xml: Xml resource to be parsed
        :param xpath: Xpath to use to retrieve the xml node
        """

    @staticmethod
    def parse_metadata(obj, xml, _cls_dict=_CLASSES_DICT):
        """ Parse a resource to feed the object

        :param obj: Obj to set metadata of
        :type obj: XmlCtsTextMetadata
        :param xml: An xml representation object
        :type xml: lxml.etree._Element
        :param _cls_dict: Dictionary of classes to generate subclasses
        """

        for child in xml.xpath("ti:description", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_cts_property("description", child.text, lg)

        for child in xml.xpath("ti:label", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_cts_property("label", child.text, lg)

        obj.citation = _cls_dict.get("citation", XmlCtsCitation).ingest(xml, obj.citation, "ti:online/ti:citationMapping/ti:citation")

        # Added for commentary
        for child in xml.xpath("ti:about", namespaces=XPATH_NAMESPACES):
            obj.set_link(RDF_NAMESPACES.CTS.term("about"), child.get('urn'))

        __parse_structured_metadata__(obj, xml)

        """
        online = xml.xpath("ti:online", namespaces=NS)
        if len(online) > 0:
            online = online[0]
            obj.docname = online.get("docname")
            for validate in online.xpath("ti:validate", namespaces=NS):
                obj.validate = validate.get("schema")
            for namespaceMapping in online.xpath("ti:namespaceMapping", namespaces=NS):
                obj.metadata["namespaceMapping"][namespaceMapping.get("abbreviation")] = namespaceMapping.get("nsURI")
        """

    def __init__(self, *args, **kwargs):
        super(XmlCtsTextMetadata, self).__init__(*args, **kwargs)
        self._path = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

class XmlCtsEditionMetadata(cts.CtsEditionMetadata, XmlCtsTextMetadata):
    """ Create an edition subtyped CtsTextMetadata object
    """
    @staticmethod
    def parse(resource, parent=None, _cls_dict=_CLASSES_DICT):
        xml = xmlparser(resource)
        o = _cls_dict.get("edition", XmlCtsEditionMetadata)(urn=xml.get("urn"), parent=parent)
        type(o).parse_metadata(o, xml)

        return o


class XmlCtsTranslationMetadata(cts.CtsTranslationMetadata, XmlCtsTextMetadata):
    """ Create a translation subtyped CtsTextMetadata object
    """
    @staticmethod
    def parse(resource, parent=None, _cls_dict=_CLASSES_DICT):
        xml = xmlparser(resource)
        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")

        o = _cls_dict.get("translation", XmlCtsTranslationMetadata)(urn=xml.get("urn"), parent=parent)
        if lang is not None:
            o.lang = lang
        type(o).parse_metadata(o, xml)
        return o


class XmlCtsCommentaryMetadata(cts.CtsCommentaryMetadata, XmlCtsTextMetadata):
    """ Create a commentary subtyped PrototypeText object
    """
    @staticmethod
    def parse(resource, parent=None, _cls_dict=_CLASSES_DICT):
        xml = xmlparser(resource)
        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")

        o = _cls_dict.get("commentary", XmlCtsCommentaryMetadata)(urn=xml.get("urn"), parent=parent)
        if lang is not None:
            o.lang = lang
        type(o).parse_metadata(o, xml)
        return o


class XmlCtsWorkMetadata(cts.CtsWorkMetadata):
    """ Represents a CTS Textgroup in XML
    """

    @staticmethod
    def parse(resource, parent=None, _cls_dict=_CLASSES_DICT, _with_children=False):
        """ Parse a resource

        :param resource: Element rerpresenting a work
        :param type: basestring, etree._Element
        :param parent: Parent of the object
        :type parent: XmlCtsTextgroupMetadata
        :param _cls_dict: Dictionary of classes to generate subclasses
        """
        xml = xmlparser(resource)
        o = _cls_dict.get("work", XmlCtsWorkMetadata)(urn=xml.get("urn"), parent=parent)

        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
            o.lang = lang

        for child in xml.xpath("ti:title", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_cts_property("title", child.text, lg)

        # Parse children
        children = []
        children.extend(xpathDict(
            xml=xml, xpath='ti:edition',
            cls=_cls_dict.get("edition", XmlCtsEditionMetadata), parent=o,
            _cls_dict=_cls_dict
        ))
        children.extend(xpathDict(
            xml=xml, xpath='ti:translation',
            cls=_cls_dict.get("translation", XmlCtsTranslationMetadata), parent=o,
            _cls_dict=_cls_dict
        ))
        # Added for commentary
        children.extend(xpathDict(
            xml=xml, xpath='ti:commentary',
            cls=_cls_dict.get("commentary", XmlCtsCommentaryMetadata), parent=o,
            _cls_dict=_cls_dict
        ))

        __parse_structured_metadata__(o, xml)

        if _with_children:
            return o, children
        return o


class XmlCtsTextgroupMetadata(cts.CtsTextgroupMetadata):
    """ Represents a CTS Textgroup in XML
    """

    @staticmethod
    def parse(resource, parent=None, _cls_dict=_CLASSES_DICT):
        """ Parse a textgroup resource

        :param resource: Element representing the textgroup
        :param parent: Parent of the textgroup
        :param _cls_dict: Dictionary of classes to generate subclasses
        """
        xml = xmlparser(resource)
        o = _cls_dict.get("textgroup", XmlCtsTextgroupMetadata)(urn=xml.get("urn"), parent=parent)

        for child in xml.xpath("ti:groupname", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_cts_property("groupname", child.text, lg)

        # Parse Works
        xpathDict(xml=xml, xpath='ti:work', cls=_cls_dict.get("work", XmlCtsWorkMetadata), parent=o)

        __parse_structured_metadata__(o, xml)
        return o


class XmlCtsTextInventoryMetadata(cts.CtsTextInventoryMetadata):
    """ Represents a CTS Inventory file
    """

    @staticmethod
    def parse(resource, _cls_dict=_CLASSES_DICT):
        """ Parse a resource

        :param resource: Element representing the text inventory
        :param _cls_dict: Dictionary of classes to generate subclasses
        """
        xml = xmlparser(resource)
        o = _cls_dict.get("inventory", XmlCtsTextInventoryMetadata)(name=xml.xpath("//ti:TextInventory", namespaces=XPATH_NAMESPACES)[0].get("tiid") or "")
        # Parse textgroups
        xpathDict(xml=xml, xpath='//ti:textgroup', cls=_cls_dict.get("textgroup", XmlCtsTextgroupMetadata), parent=o)
        return o