from setuptools import setup
from setuptools import find_packages

import sys

version = '5.1rc2.dev0'

INSTALL_REQUIRES = [
    'setuptools',
    'AccessControl >= 4.0b1',
    'Acquisition',
    'DateTime',
    'ExtensionClass',
    'Pillow',
    'Products.CMFCore',
    'Products.CMFDiffTool',
    'Products.CMFDynamicViewFTI',
    'Products.CMFEditions',
    'Products.CMFFormController',
    'Products.CMFQuickInstallerTool',
    'Products.CMFUid',
    'Products.DCWorkflow',
    'Products.ExtendedPathIndex',
    'Products.GenericSetup >= 2.0.dev0',
    'Products.MimetypesRegistry',
    'Products.PlonePAS',
    'Products.PluggableAuthService',
    'Products.PluginRegistry',
    'Products.PortalTransforms',
    'Products.ResourceRegistries',
    'Products.Sessions',
    'Products.SiteErrorLog',
    'Products.TemporaryFolder',
    'Products.contentmigration',
    'Products.statusmessages',
    'ZODB3',
    'Zope >= 4.0b2',
    'borg.localrole',
    'five.customerize',
    'five.localsitemanager',
    'mockup',
    'plone.api >= 1.4.4',
    'plone.app.content',
    'plone.app.contentlisting',
    'plone.app.contentmenu >= 1.1.6dev-r22380',
    'plone.app.contentrules',
    'plone.app.contenttypes',
    'plone.app.controlpanel',
    'plone.app.customerize',
    'plone.app.dexterity',
    'plone.app.discussion',
    'plone.app.folder',
    'plone.app.i18n',
    'plone.app.multilingual',
    'plone.app.layout >=1.1.7dev-r23744',
    'plone.app.linkintegrity >=1.0.3',
    'plone.app.locales',
    'plone.app.portlets',
    'plone.app.redirector',
    'plone.app.registry',
    'plone.app.theming',
    'plone.app.users',
    'plone.app.uuid',
    'plone.app.viewletmanager',
    'plone.app.vocabularies',
    'plone.app.workflow',
    'plone.batching',
    'plone.browserlayer >= 1.0rc4',
    'plone.contentrules',
    'plone.i18n',
    'plone.indexer',
    'plone.intelligenttext',
    'plone.locking',
    'plone.memoize',
    'plone.outputfilters',
    'plone.portlet.collection',
    'plone.portlet.static',
    'plone.portlets',
    'plone.protect >= 3.0.0a1',
    'plone.registry',
    'plone.schema',
    'plone.session',
    'plone.subrequest',
    'plone.theme',
    'plonetheme.barceloneta',
    'pyScss',
    'six',
    'slimit',
    'transaction',
    'z3c.autoinclude',
    'zope.app.locales >= 3.6.0',
    'zope.cachedescriptors',
    'zope.component',
    'zope.container',
    'zope.deferredimport',
    'zope.deprecation',
    'zope.dottedname',
    'zope.event',
    'zope.i18n',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.location',
    'zope.pagetemplate',
    'zope.publisher',
    'zope.site',
    'zope.structuredtext',
    'zope.tal',
    'zope.tales',
    'zope.traversing',
]

PY2_ONLY = [
    'Products.ExternalEditor',
    'ZServer',
]

if sys.version_info[0] == 2:
    INSTALL_REQUIRES += PY2_ONLY

setup(
    name='Products.CMFPlone',
    version=version,
    description="The Plone Content Management System (core)",
    long_description=open("README.rst").read() + "\n" +
    open("CHANGES.rst").read(),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.1",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords='Plone CMF python Zope',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='http://plone.org/',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        archetypes=[
            'Products.ATContentTypes',
        ],
        test=[
            'lxml',
            'mock',
            'plone.app.robotframework>0.9.16',
            'robotframework-debuglibrary',
            'plone.app.testing',
            'zope.globalrequest',
            'zope.testing',
        ]
    ),
    install_requires=INSTALL_REQUIRES,
    entry_points="""\
      [console_scripts]
      plone-compile-resources = Products.CMFPlone._scripts.compile_resources:main
      """
)
