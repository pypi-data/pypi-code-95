# copyright 2019-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

options = (
    ('saml-allow-unsolicited', {
        'type': 'yn',
        'default': True,
        'help': "Don't verify that the incoming requests originate from us "
                "via the built-in cache for authn request ids in pysaml2",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-authn-requests-signed', {
        'type': 'yn',
        'default': False,
        'help': "Indicates if the Authentication Requests sent by this SP "
                "should be signed by default.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-logout-requests-signed', {
        'type': 'yn',
        'default': True,
        'help': "Indicates if this entity will sign the Logout Requests "
                "originated from it.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-want-assertions-signed', {
        'type': 'yn',
        'default': True,
        'help': "Indicates if this SP wants the IdP to send the assertions "
                "signed. This sets the WantAssertionsSigned attribute of the "
                "SPSSODescriptor node of the metadata so the IdP will know "
                "this SP preference.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-want-response-signed', {
        'type': 'yn',
        'default': False,
        'help': "Indicates that Authentication Responses to this SP must be "
                "signed. If set to True, the SP will not consume any SAML "
                "Responses that are not signed.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-register-unknown-user', {
        'type': 'yn',
        'default': False,
        'help': "Allow to register a new user if this one does not exist in "
                "current database.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-register-default-group', {
        'type': 'string',
        'default': 'guests',
        'help': "Set the default group to register new user if the "
                "saml-register-unknown-user option was activated.",
        'group': 'saml',
        'level': 5,
    }),
    ('saml-register-default-password', {
        'type': 'string',
        'default': 'empty',
        'help': "Set the default password system to use if the "
                "saml-register-unknown-user option was activated. Available "
                "modes: empty (no password), random (set a randomize password "
                "based on hashed string).",
        'group': 'saml',
        'level': 5,
    }),
)
