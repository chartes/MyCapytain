MyCapytain API Documentation
============================

Utilities, metadata and references
##################################

Module common contains tools such as a namespace dictionary as well as cross-implementation objects, like URN, Citations...

Base
****

.. automodule:: MyCapytain.common.base
    :noindex:
    :members:

Constants
*********

.. automodule:: MyCapytain.common.constants
    :noindex:
    :members:

URN, References and Citations
*****************************

MyCapytain Base Objects
+++++++++++++++++++++++

.. autoclass:: MyCapytain.common.reference.NodeId
.. autoclass:: MyCapytain.common.reference.BaseCitationSet
.. autoclass:: MyCapytain.common.reference.BaseReference
.. autoclass:: MyCapytain.common.reference.BaseReferenceSet

Canonical Text Services Objects
+++++++++++++++++++++++++++++++

.. autoclass:: MyCapytain.common.reference.Citation
.. autoclass:: MyCapytain.common.reference.CtsReference
.. autoclass:: MyCapytain.common.reference.CtsReferenceSet

Distributed Text Services Objects
+++++++++++++++++++++++++++++++++

.. autoclass:: MyCapytain.common.reference.URN
.. autoclass:: MyCapytain.common.reference.DtsCitation
.. autoclass:: MyCapytain.common.reference.DtsCitationSet


Metadata containers
*******************

.. automodule:: MyCapytain.common.metadata
    :noindex:
    :members:
    :inherited-members:

Utilities
*********

.. automodule:: MyCapytain.common.utils
    :noindex:
    :members:

API Retrievers
##############

Module endpoints contains prototypes and implementation of retrievers in MyCapytain

CTS 5 API
*********

.. automodule:: MyCapytain.retrievers.cts5
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Prototypes
**********

.. automodule:: MyCapytain.retrievers.prototypes
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:


Resolvers
#########

Remote CTS API
**************

.. autoclass:: MyCapytain.resolvers.cts.api.HttpCtsResolver
    :members:

Local CapiTainS Guidelines CTS Resolver
***************************************

.. autoclass:: MyCapytain.resolvers.cts.local.CtsCapitainsLocalResolver
    :members:

Dispatcher
**********

.. autoclass:: MyCapytain.resolvers.utils.CollectionDispatcher
    :members:
    :noindex:

Prototypes
**********

.. autoclass:: MyCapytain.resolvers.prototypes.Resolver
    :members:
    :noindex:


Texts and inventories
#####################

Text
****

TEI based texts
+++++++++++++++

.. autoclass:: MyCapytain.resources.texts.base.tei.TEIResource
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Locally read text
+++++++++++++++++

.. autoclass:: MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsPassage
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: MyCapytain.resources.texts.local.capitains.cts.__SimplePassage__
    :members:
    :show-inheritance:
    :inherited-members:

CTS API Texts
+++++++++++++

Formerly MyCapytain.resources.texts.api (< 2.0.0)

.. autoclass:: MyCapytain.resources.texts.remote.cts.CtsText
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: MyCapytain.resources.texts.remote.cts.CtsPassage
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Collections
***********

Metadata
++++++++

.. automodule:: MyCapytain.resources.prototypes.metadata
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

CTS inventory
+++++++++++++

.. automodule:: MyCapytain.resources.collections.cts
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

CTS Inventory Prototypes
++++++++++++++++++++++++

.. automodule:: MyCapytain.resources.prototypes.cts.inventory
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Text Prototypes
+++++++++++++++

.. automodule:: MyCapytain.resources.prototypes.text
    :noindex:
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:
