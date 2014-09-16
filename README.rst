===========================
``gs.group.member.request``
===========================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Request membership of a private group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2013-03-21
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 3.0 New Zealand License`_
  by `OnlineGroups.Net`_.

Introduction
============

This is the code to allow a person to request_ membership of a private
group, and to allow the group administrator to respond_ to the request,
adding the person as a new member or declining the request. Only *private*
groups have this feature:

* In *public* groups anyone can join, without needing the approval of an
  administrator.

* Only the members can see the existence of *secret* groups, so everyone
  has to be invited.

Request
=======

The request is made up of two parts: the `request page`_ is used to
formulate the request, and the `request notification`_ that is sent to the
group administrator.

Request Page
------------

The request page, ``request.html`` in the Group context, is shown to
logged-in non-members when viewing a private group. To simplify the code,
the sign-up system [#signup]_ is hacked on the front to ensure that the
person requesting membership has a profile and is logged in. It is not
pretty, and I am not proud. (The group-info viewlet [#info]_ handles the
linking to the request page.)

The person requesting membership has a chance to write a short message
explaining who they are, and why they should become a member of the
group. (It is a bit like an invitation in reverse [#invite]_.) This message
is sent as part of the `request notification`_.

Request Notification
--------------------

The request notification is sent to the group administrator by the `request
page`_. It is made up of HTML and plain-text versions, supplied by the
pages ``request_message.html`` and ``request_message.txt`` in the Group
context. The notification introduces the supplicant, and links the group
administrator to the page that allows him or her to respond_.

Each page takes four parameters, passed as form-fields:

``userId``:
  The identifier of the person making the request.

``email``:
  The email address of the person making the request.

``mesg``: 
  The message that the person making the request wrote to the group
  administrator.

``adminId``:
  The identifier of the group administrator receiving the request.

Respond
=======

The response part of the system is made up of the `response page`_ and two
different `response notifications`_.

Response Page
-------------

The Response page, ``respond.html`` in the Group context, is linked to from
the member-management links on the Group page. The link has a very low
weight (0) and is only shown when there are outstanding requests to respond
to.

The Response page is modelled on the page that participants use to accept
and decline invitations to join a group [#inviteRespond]_: it lists all the
people who have requested membership, their messages, and for each gives
the option of accepting or declining the request. Depending on the option
selected the supplicant will receive one of two different `response
notifications`_.

Response Notifications
----------------------

If the group administrator accepts the request of the supplicant then the
person is joined to the group, and he or she receives a Group Welcome
notification [#join]_.

If the group administrator declines the request of the supplicant then the
person is sent a decline message, provided by the pages
``decline_message.html`` and ``decline_message.txt`` in the Group
context. Both pages take the same parameters as the `request
notification`_.

Resources
=========

- Code repository: https://source.iopen.net/groupserver/gs.group.member.request
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Creative Commons Attribution-Share Alike 3.0 New Zealand License:
   http://creativecommons.org/licenses/by-sa/3.0/nz/

.. [#signup] See ``gs.profile.signup.base``
             <https://source.iopen.net/groupserver/gs.profile.signup.base>

.. [#info] See ``gs.group.member.info``
           <https://source.iopen.net/groupserver/gs.group.member.info>

.. [#invite] See ``gs.group.member.invite.base``
             <https://source.iopen.net/groupserver/gs.group.member.invite.base>

.. [#inviteRespond] See ``gs.profile.invite``
                    <https://source.iopen.net/groupserver/gs.profile.invite>

.. [#join] See ``gs.group.member.join``
           <https://source.iopen.net/groupserver/gs.group.member.join>
