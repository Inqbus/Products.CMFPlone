# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl import Permissions
from AccessControl import Unauthorized
from Acquisition import aq_base
from App.class_init import InitializeClass
from ComputedAttribute import ComputedAttribute
from plone.i18n.locales.interfaces import IMetadataLanguageAvailability
from Products.CMFCore import permissions
from Products.CMFCore.PortalObject import PortalObjectBase
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.DublinCore import DefaultDublinCoreImpl
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from Products.CMFPlone.permissions import AddPortalContent
from Products.CMFPlone.permissions import AddPortalFolders
from Products.CMFPlone.permissions import ListPortalMembers
from Products.CMFPlone.permissions import ModifyPortalContent
from Products.CMFPlone.permissions import ReplyToItem
from Products.CMFPlone.permissions import View
from Products.CMFPlone.PloneFolder import OrderedContainer
from Products.CMFPlone.PloneFolder import ReplaceableWrapper
from webdav.NullResource import NullResource
from zope.component import queryUtility
from zope.interface import implementer

from zope.interface import classImplementsOnly, implementedBy

# hackydihack
+from plone.dexterity.content import Container
+from five.localsitemanager.registry import PersistentComponents
+from Products.CMFCore.interfaces import ISiteRoot, IContentish
+from Products.Five.component.interfaces import IObjectManagerSite
+from Products.CMFCore.permissions import AddPortalMember
+from Products.CMFCore.permissions import SetOwnPassword
+from Products.CMFCore.permissions import SetOwnProperties
+from Products.CMFCore.permissions import MailForgottenPassword
+from Products.CMFCore.permissions import RequestReview
+from Products.CMFCore.permissions import ReviewPortalContent
+from Products.CMFCore.Skinnable import SkinnableObjectManager

from zope.event import notify
from zope.component.interfaces import ComponentLookupError

from zope.traversing.interfaces import BeforeTraverseEvent


PORTAL_SKINS_TOOL_ID = 'portal_skins'

@implementer(IPloneSiteRoot, ISiteRoot, ISyndicatable, IObjectManagerSite)
class PloneSite(Container, SkinnableObjectManager, UniqueObject):
    """ The Plone site object. """

    security = ClassSecurityInfo()
    meta_type = portal_type = 'Plone Site'

    # Ensure certain attributes come from the correct base class.
    _checkId = SkinnableObjectManager._checkId

    def __getattr__(self, name):
        try:
            return SkinnableObjectManager.__getattr__(self, name)
        except AttributeError:
            return super(PloneSite, self).__getattr__(name)

    # Removes the 'Components Folder'

    manage_options = (
        Container.manage_options[:2] +
        Container.manage_options[3:])

    __ac_permissions__ = (
        (AddPortalMember, ()),
        (SetOwnPassword, ()),
        (SetOwnProperties, ()),
        (MailForgottenPassword, ()),
        (RequestReview, ()),
        (ReviewPortalContent, ()),

        (AddPortalContent, ()),
        (AddPortalFolders, ()),
        (ListPortalMembers, ()),
        (ReplyToItem, ()),
        (View, ('isEffective',)),
        (ModifyPortalContent, ('manage_cutObjects', 'manage_pasteObjects',
                               'manage_renameForm', 'manage_renameObject',
                               'manage_renameObjects')))

    security.declareProtected(Permissions.copy_or_move, 'manage_copyObjects')

    manage_renameObject = OrderedContainer.manage_renameObject

    moveObject = OrderedContainer.moveObject
    moveObjectsByDelta = OrderedContainer.moveObjectsByDelta

    # Switch off ZMI ordering interface as it assumes a slightly
    # different functionality
    has_order_support = 0
    management_page_charset = 'utf-8'
    _default_sort_key = 'id'
    _properties = (
        {'id': 'title', 'type': 'string', 'mode': 'w'},
        {'id': 'description', 'type': 'text', 'mode': 'w'},
        {'id': 'add_permission', 'type': 'text', 'mode': 'w'},
    )
    title = ''
    description = ''
    icon = 'misc_/CMFPlone/tool.gif'

    # From PortalObjectBase.__init__
    def __init__(self, id, title=''):
        super(PloneSite, self).__init__(id, title=title)
        components = PersistentComponents('++etc++site')
        components.__parent__ = self
        self.setSiteManager(components)

    # From PortalObjectBase.__init__
    def getSkinsFolderName(self):
        return PORTAL_SKINS_TOOL_ID

    # From PortalObjectBase.__init__
    def __before_publishing_traverse__(self, arg1, arg2=None):
        """ Pre-traversal hook.
        """
        # XXX hack around a bug(?) in BeforeTraverse.MultiHook
        REQUEST = arg2 or arg1

        try:
            notify(BeforeTraverseEvent(self, REQUEST))
        except ComponentLookupError:
            # allow ZMI access, even if the portal's site manager is missing
            pass
        self.setupCurrentSkin(REQUEST)

    def __browser_default__(self, request):
        """ Set default so we can return whatever we want instead
        of index_html """
        return getToolByName(self, 'plone_utils').browserDefault(self)

    def index_html(self):
        """ Acquire if not present. """
        request = getattr(self, 'REQUEST', None)
        if request is not None and 'REQUEST_METHOD' in request:
            if request.maybe_webdav_client:
                method = request['REQUEST_METHOD']
                if method in ('PUT', ):
                    # Very likely a WebDAV client trying to create something
                    return ReplaceableWrapper(NullResource(self, 'index_html'))
                elif method in ('GET', 'HEAD', 'POST'):
                    # Do nothing, let it go and acquire.
                    pass
                else:
                    raise AttributeError('index_html')
        # Acquire from skin.
        _target = self.__getattr__('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

    def manage_beforeDelete(self, container, item):
        # Should send out an Event before Site is being deleted.
        self.removal_inprogress = 1
        PloneSite.inheritedAttribute('manage_beforeDelete')(self, container,
                                                            item)

    def view(self):
        """ Ensure that we get a plain view of the object, via a delegation to
        __call__(), which is defined in BrowserDefaultMixin
        """
        return self()

    security.declareProtected(permissions.AccessContentsInformation,
                              'folderlistingFolderContents')

    def folderlistingFolderContents(self, contentFilter=None):
        """Calls listFolderContents in protected only by ACI so that
        folder_listing can work without the List folder contents permission.

        This is copied from Archetypes Basefolder and is needed by the
        reference browser.
        """
        return self.listFolderContents(contentFilter)

    security.declarePublic('availableLanguages')

    def availableLanguages(self):
        util = queryUtility(IMetadataLanguageAvailability)
        languages = util.getLanguageListing()
        languages.sort(lambda x, y: cmp(x[1], y[1]))
        # Put language neutral at the top.
        languages.insert(0, (u'', _(u'Language neutral (site default)')))

        return languages

    def isEffective(self, date):
        # Override DefaultDublinCoreImpl's test, since we are always viewable.
        return 1

    # Ensure portals don't get cataloged.
    def indexObject(self):
        pass

    def unindexObject(self):
        pass

    def reindexObject(self, idxs=None):
        pass

    def reindexObjectSecurity(self, skip_self=False):
        pass

InitializeClass(PloneSite)
