from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.utils import _getAuthenticatedUser, _checkPermission
from Products.CMFCore.CMFCorePermissions import AccessInactivePortalContent
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass
from DateTime import DateTime

class CatalogTool(BaseTool):

    meta_type = ToolNames.CatalogTool
    security = ClassSecurityInfo()

    def catalogObject(self, object, uid, threshold=None, idxs=[]):
        """ 
        Unwraps the acquisition from an object before it is cataloged. 
        """
        if self.getProperty('unwrapobjects', None):
            object=aq_base(object)

        BaseTool.catalogObject(self, object, uid, threshold=None, idxs=[])
        
    def manage_afterAdd(self, item, container):

        if item is self:
            class args:
                def __init__(self, **kw):
                    self.__dict__.update(kw)

            # when a catalog is pasted, there is allredy a ZCTextIndex
            try:
                self.manage_addProduct[ 'ZCTextIndex' ].manage_addLexicon(
                    'plone_lexicon',
                    elements=[
                    args(group= 'Case Normalizer' , name= 'Case Normalizer' ),
                    args(group= 'Stop Words' , name= " Don't remove stop words" ),
                    args(group= 'Word Splitter' , name= "Unicode Whitespace splitter" ),
                    ]
                    )
            except:
                pass

            extra = args( doc_attr = 'SearchableText',
                          lexicon_id = 'plone_lexicon',
                          index_type  = 'Okapi BM25 Rank' )

            self.manage_delIndex(['SearchableText'])
            self.manage_addIndex('SearchableText', 'ZCTextIndex', extra=extra)


    def _listAllowedRolesAndUsers( self, user ):
        result = list( user.getRoles() )
        try:
            result += map(lambda x: "user:%s" % x, user.getGroups())
        except:
            pass
        result.append( 'Anonymous' )
        result.append( 'user:%s' % user.getId() )
        return result

    # searchResults has inherited security assertions.
    def searchResults(self, REQUEST=None, **kw):
        """
            Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.
        """
        user = _getAuthenticatedUser(self)
        kw[ 'allowedRolesAndUsers' ] = self._listAllowedRolesAndUsers( user )

        if not _checkPermission( AccessInactivePortalContent, self ):
            base = aq_base( self )
            now = DateTime()
            if hasattr( base, 'addIndex' ):   # Zope 2.4 and above
                kw[ 'effective' ] = { 'query' : now, 'range' : 'max' }
                kw[ 'expires'   ] = { 'query' : now, 'range' : 'min' }
            else:                             # Zope 2.3
                kw[ 'effective'      ] = kw[ 'expires' ] = now
                kw[ 'effective_usage'] = 'range:max'
                kw[ 'expires_usage'  ] = 'range:min'

        return apply(BaseTool.searchResults, (self, REQUEST), kw)

    __call__ = searchResults

CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)
