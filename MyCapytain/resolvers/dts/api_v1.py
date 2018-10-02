# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resolvers.cts.remote
   :synopsis: Resolver built for CTS APIs

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from typing import Union, Optional, Any, Dict
import re

from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.common.reference import BaseReference, BaseReferenceSet, \
    DtsReference, DtsReferenceSet, DtsCitation
from MyCapytain.retrievers.dts import HttpDtsRetriever
from MyCapytain.common.utils.dts import parse_metadata
from MyCapytain.resources.collections.dts import DtsCollection

from pyld.jsonld import expand


__all__ = [
    "HttpDtsResolver"
]

_empty = [{"@value": None}]
_re_page = re.compile("page=(\d+)")


def _parse_ref(ref_dict, default_type :str =None):
    if "https://w3id.org/dts/api#ref" in ref_dict:
        refs = ref_dict["https://w3id.org/dts/api#ref"][0]["@value"],
    elif "https://w3id.org/dts/api#start" in ref_dict and \
         "https://w3id.org/dts/api#end" in ref_dict:
        refs = (
            ref_dict["https://w3id.org/dts/api#start"][0]["@value"],
            ref_dict["https://w3id.org/dts/api#end"][0]["@value"]
        )
    else:
        return None  # Maybe Raise ?
    type_ = default_type
    if "https://w3id.org/dts/api#citeType" in ref_dict:
        type_ = ref_dict["https://w3id.org/dts/api#citeType"][0]["@value"]

    obj = DtsReference(*refs, type_=type_)
    parse_metadata(obj.metadata, ref_dict)

    return obj


class HttpDtsResolver(Resolver):
    """ HttpDtsResolver provide a resolver for DTS API http endpoint.

    :param endpoint: DTS API Retriever
    """
    def __init__(self, endpoint: Union[str, HttpDtsRetriever]):
        if not isinstance(endpoint, HttpDtsRetriever):
            endpoint = HttpDtsRetriever(endpoint)
        self._endpoint = endpoint

    @property
    def endpoint(self) -> HttpDtsRetriever:
        """ DTS Endpoint of the resolver

        :return: DTS Endpoint
        :rtype: HttpDtsRetriever
        """
        return self._endpoint

    def getMetadata(self, objectId: str=None, **filters) -> DtsCollection:
        req = self.endpoint.get_collection(objectId)
        req.raise_for_status()

        collection = DtsCollection.parse(req.json())
        # Pagination is not completed upon first query.
        # Pagination will be treated direction in the DtsCollection

        return collection

    def getReffs(
            self,
            textId: str,
            level: int=1,
            subreference: Union[str, BaseReference]=None,
            include_descendants: bool=False,
            additional_parameters: Optional[Dict[str, Any]]=None
    ) -> DtsReferenceSet:
        if not additional_parameters:
            additional_parameters = {}

        references = []
        default_type = None
        level_ = level

        page = 1
        while page:
            kwargs = dict(
                level=level, ref=subreference,
                exclude=additional_parameters.get("exclude", None),
                group_by=additional_parameters.get("groupBy", 1)
            )
            if page != 1:
                kwargs["page"] = page

            response = self.endpoint.get_navigation(textId, **kwargs)
            response.raise_for_status()

            data = response.json()
            data = expand(data)
            if not len(data):
                raise Exception("We'll see this one later")  # toDo: What error should it be ?
            data = data[0]

            level_ = data.get("https://w3id.org/dts/api#level", _empty)[0]["@value"]
            default_type = data.get("https://w3id.org/dts/api#citeType", _empty)[0]["@value"]
            members = data.get("https://www.w3.org/ns/hydra/core#member", [])

            references.extend([
                _parse_ref(ref, default_type=default_type)
                for ref in members
            ])

            page = None
            if "https://www.w3.org/ns/hydra/core#view" in data:
                if "https://www.w3.org/ns/hydra/core#next" in data["https://www.w3.org/ns/hydra/core#view"][0]:
                    page = _re_page.findall(
                        data["https://www.w3.org/ns/hydra/core#view"]
                            [0]["https://www.w3.org/ns/hydra/core#next"]
                            [0]["@value"]
                    )[0]

        citation = None
        if default_type:
            citation = DtsCitation(name=default_type)

        reffs = DtsReferenceSet(
            *references,
            level=level_,
            citation=citation
        )
        return reffs
