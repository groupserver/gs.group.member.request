# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

setup(name='gs.group.member.request',
    version=version,
    description="Request membership in a GroupServer group",
    long_description=open("README.txt").read() + "\n" +
                      open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux"
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='groupserver member request private secret',
    author='Michael JasonSmith',
    author_email='mpj17@onlinegroups.net',
    url='http://groupserver.org/',
    license='other',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs', 'gs.group', 'gs.group.member'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pytz',
        'sqlalchemy',
        'zope.cachedescriptors',
        'zope.component',
        'zope.formlib',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'zope.sqlalchemy',
        'Zope2',
        'gs.content.email.base',
        'gs.content.email.layout'
        'gs.content.form',
        'gs.database',
        'gs.group.base',
        'gs.group.member.join',
        'gs.group.member.viewlet',
        'gs.profile.notify',
        'gs.profile.email.base',
        'gs.profile.notify',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,)
