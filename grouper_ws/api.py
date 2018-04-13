from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import base64
import json
import requests
import logging
import six

try: # Py3
    from urllib.parse import quote, urljoin
except ImportError: # Py2
    from urlparse import urljoin
    from urllib import quote

try:
    from requests_negotiate import HTTPNegotiateAuth as HTTPDefaultAuth
except ImportError:
    try:
        from requests_kerberos import HTTPKerberosAuth as HTTPDefaultAuth
    except ImportError:
        def HTTPNegotiateAuthMock(*args, **kwargs):
            return None
        HTTPDefaultAuth = HTTPNegotiateAuthMock

from .groups import *
from .stems import *
from .subjects import *


DEFAULT_SUBJECT_ATTRIBUTES = [
    "description",
    "oakpersonid",
    "oakoxfordssousername",
    "name"
]

logger = logging.getLogger(__name__)

def bool_to_tf_str(b):
    if b:
        return 'T'
    return 'F'

def tf_str_to_bool(s):
    if s == 'T':
        return True
    return False

def member_to_subject_lookup(member):
    if isinstance(member, six.text_type):
        return {
        'subjectId': member,
        }
    elif type(member) == tuple:
        return {
            'subjectId': member[0],
            'subjectSourceId': member[1],
        }
    elif isinstance(member, Subject):
        return member.get_subject_lookup()
    raise Exception("member_to_subject_lookup(): Invalid member value")

def str_to_stem(stem):
    if isinstance(stem, Stem):
        return stem
    else:
        return Stem(str(stem))

def str_to_group(group):
    if isinstance(group, Group):
        return group
    else:
        return Group(str(group))


class Grouper(object):
    def __init__(self, host_name, base_url, auth=HTTPDefaultAuth()):
        self.host_name = host_name
        self.base_url = urljoin('https://' + self.host_name, base_url)
        self.auth = auth
        self._session = requests.Session()

    def request(self, method, url, data):
        """
        Perform an authenticated request against the remote Grouper instance.
        """
        headers = {
            'Content-type': 'text/x-json',
        }
        real_url = urljoin(self.base_url, url)
        http_response = method(
            real_url,
            headers=headers,
            data=json.dumps(data),
            auth=self.auth
        )
        logger.debug(http_response)
        return http_response.json()

    def add_members(self, group, members, replace_existing=False):
        if isinstance(group, Group):
            group = group.group_name

        url = 'servicesRest/v2_1_005/groups/{0}/members'.format(quote(group, safe=''))

        members_list = [member_to_subject_lookup(member) for member in members]

        data = {
            'WsRestAddMemberRequest': {
                'replaceAllExisting': bool_to_tf_str(replace_existing),
                'subjectLookups': members_list,
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def find_groups(self, query):
        url = 'servicesRest/v2_1_005/groups/'

        data = {
            'WsRestFindGroupsRequest': {
                'wsQueryFilter': query.to_json_dict(),
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def find_stems(self, query):
        url = 'servicesRest/v2_1_005/stems/'

        data = {
            'WsRestFindStemsRequest': {
                'wsStemQueryFilter': query.to_json_dict(),
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def lookup_groups(self, groups):
        url = 'servicesRest/v2_1_005/groups/'
        group_list = [{'groupName': group} for group in groups]

        data = {
            'WsRestFindGroupsRequest': {
                'wsGroupLookups': group_list,
                'includeGroupDetail': 'T',
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def has_members(self, group, members):
        if isinstance(group, Group):
            group = group.group_name

        url = 'servicesRest/v2_1_005/groups/{0}/members'.format(quote(group, safe=''))

        members_list = [member_to_subject_lookup(member) for member in members]

        data = {
            'WsRestHasMemberRequest': {
                'subjectLookups': members_list,
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_members(self, groups, subject_attributes=DEFAULT_SUBJECT_ATTRIBUTES,
        details=True, page_size=None, page=1):
        url = 'servicesRest/v2_1_005/groups'
        group_list = [{'groupName': group} for group in groups]

        data = {
            'WsRestGetMembersRequest': {
                'subjectAttributeNames': subject_attributes,
                'wsGroupLookups': group_list,
                'includeSubjectDetail': bool_to_tf_str(details),
            },
        }
        if page_size is not None:
            if page < 1:
                page = 1
            data['WsRestGetMembersRequest']['pageSize'] = str(page_size)
            data['WsRestGetMembersRequest']['pageNumber'] = str(page)
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_subjects(self, subjects, subject_attributes=DEFAULT_SUBJECT_ATTRIBUTES):
        url = 'servicesRest/v2_1_005/subjects'

        subjects_list = [member_to_subject_lookup(subject) for subject in subjects]

        data = {
            'WsRestGetSubjectsRequest': {
                'subjectAttributeNames': subject_attributes,
                'wsSubjectLookups': subjects_list,
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_group_memberships(self, group, member_filter='All', subject_attributes=DEFAULT_SUBJECT_ATTRIBUTES, details=True):
        if isinstance(group, Group):
            group = group.group_name

        url = 'servicesRest/v2_1_005/groups/{0}/memberships'.format(quote(group, safe=''))
        member_filter_values = ['All', 'Effective', 'Immediate', 'Composite', 'NonImmediate']
        if member_filter not in member_filter_values:
            raise Exception("member_filter must be in '{0}'".format(member_filter_values))

        data = {
            'WsRestGetMembershipsRequest': {
                'subjectAttributeNames': subject_attributes,
                'memberFilter': 'All',
                'includeGroupDetail': 'T',
                'includeSubjectDetail': bool_to_tf_str(details),
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_memberships_for_subjects(
        self, members, member_filter='All',
        subject_attributes=DEFAULT_SUBJECT_ATTRIBUTES,
        group_details=False
    ):
        url = 'servicesRest/v2_1_005/memberships'

        members_list = [member_to_subject_lookup(member) for member in members]

        member_filter_values = ['All', 'Effective', 'Immediate', 'Composite', 'NonImmediate']
        if member_filter not in member_filter_values:
            raise Exception("member_filter must be in '{0}'".format(member_filter_values))

        params = {
            'subjectAttributeNames': subject_attributes,
            'memberFilter': 'All',
            'includeGroupDetail': bool_to_tf_str(group_details),
            'includeSubjectDetail': 'T',
            'wsSubjectLookups': members_list,
        }
        data = {
            'WsRestGetMembershipsRequest': params,
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def save_groups(self, groups):
        url = 'servicesRest/v2_1_005/groups'

        groups = [str_to_group(group) for group in groups]

        data = {
            'WsRestGroupSaveRequest': {
                'includeGroupDetail': 'T',
                'wsGroupToSaves': [g.to_json_dict() for g in groups],
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def save_stems(self, stems):
        url = 'servicesRest/v2_1_005/stems'

        stems = [str_to_stem(stem) for stem in stems]

        data = {
            'WsRestStemSaveRequest': {
                'wsStemToSaves': [s.to_json_dict() for s in stems],
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def delete_groups(self, groups):
        url = 'servicesRest/v2_1_005/groups'

        groups = [str_to_group(group) for group in groups]

        data = {
            'WsRestGroupDeleteRequest': {
                'includeGroupDetail': 'T',
                'wsGroupLookups': [g.get_group_lookup() for g in groups],
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def delete_stems(self, stems):
        url = 'servicesRest/v2_1_005/stems'

        stems = [str_to_stem(stem) for stem in stems]

        data = {
            'WsRestStemDeleteRequest': {
                'wsStemLookups': [s.get_stem_lookup() for s in stems],
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_privileges(self, privilege_type=None, privilege_name=None,
                       stem=None, group=None, member=None):
        url = 'servicesRest/v2_1_005/grouperPrivileges'

        # Why is it that this is "Lite" only?
        data = {
            'WsRestGetGrouperPrivilegesLiteRequest': {
            },
        }
        params = {}

        if stem is not None:
            params['stemName'] = str_to_stem(stem).stem_name

        if group is not None:
            params['groupName'] = str_to_group(group).group_name

        if member is not None:
            subject_lookup = member_to_subject_lookup(member)
            params.update(subject_lookup)

        if privilege_name is not None:
            params['privilegeName'] = privilege_name

        if privilege_type is not None:
            params['privilegeType'] = privilege_type

        data['WsRestGetGrouperPrivilegesLiteRequest'].update(params)

        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def assign_privileges(self, privilege_type, privilege_names, allowed=True,
                          stem=None, group=None, members=None,
                          replace_existing=False):
        url = 'servicesRest/v2_1_005/grouperPrivileges'

        data = {
            'WsRestAssignGrouperPrivilegesRequest': {
                'includeGroupDetail': 'T',
                'includeSubjectDetail': 'T',
                'allowed': bool_to_tf_str(allowed),
            },
        }
        params = {}

        if members is not None:
            members_list = [member_to_subject_lookup(member) for member in members]
            params['wsSubjectLookups'] = members_list
        
        if stem is not None:
            stem = str_to_stem(stem)
            params['wsStemLookup'] = stem.get_stem_lookup()
        elif group is not None:
            group = str_to_group(group)
            params['wsGroupLookup'] = group.get_group_lookup()

        if members is None and stem is None and group is None:
            raise Exception("assign_privileges(): No stem, group or subject specified!")

        params['privilegeNames'] = privilege_names
        params['privilegeType'] = privilege_type
        params['replaceAllExisting'] = bool_to_tf_str(replace_existing)

        data['WsRestAssignGrouperPrivilegesRequest'].update(params)

        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def assign_attributes(self, stems=None, groups=None, attribute_assigns=None, attributes={},
                          attr_op='assign_attr', attr_value_op='assign_value'):
        """
        Assign attribute/value pairs to a list of stems or groups.
        """
        url = 'servicesRest/v2_1_005/attributeAssignments'

        if attr_op not in ['assign_attr', 'add_attr', 'remove_attr']:
            raise Exception("Unknown attribute assign operation")
        if attr_value_op not in ['assign_value', 'add_value', 'remove_value', 'replace_values']:
            raise Exception("Unknown attribute value assign operation")
        data = {
            'WsRestAssignAttributesRequest': {
                'attributeAssignOperation': attr_op,
                'wsAttributeDefNameLookups': [
                    {'name': attr} for attr in attributes
                ],
            },
        }
        params = {}

        if stems is not None:
            stems = [str_to_stem(stem).get_stem_lookup() for stem in stems]
            params['wsOwnerStemLookups'] = stems
            params['attributeAssignType'] = 'stem'
        elif groups is not None:
            groups = [str_to_group(group) for group in groups]
            params['wsOwnerGroupLookups'] = [group.get_group_lookup() for group in groups]
            params['attributeAssignType'] = 'group'
        elif attribute_assigns is not None:
            attribute_assigns = [
                {
                    'uuid': assign_uuid
                }
                for assign_uuid in attribute_assigns
            ]
            params['wsOwnerAttributeAssignLookups'] = attribute_assigns
            params['attributeAssignType'] = 'group_asgn'

        if attr_op == 'assign_attr':
            params['values'] = [
                {'valueSystem': attributes[attr]} for attr in attributes
            ]
            params['attributeAssignValueOperation'] = attr_value_op

        data['WsRestAssignAttributesRequest'].update(params)

        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_attribute_assignments(self, stems=None, groups=None, attributes=None):
        url = 'servicesRest/v2_1_005/attributeAssignments'

        data = {
            'WsRestGetAttributeAssignmentsRequest': {
                'includeAssignmentsOnAssignments': 'T',
            },
        }
        params = {}

        if attributes is not None:
            params['wsAttributeDefNameLookups'] = [
                {'name': attr} for attr in attributes
            ]
        if stems is not None:
            stems = [str_to_stem(stem).get_stem_lookup() for stem in stems]
            params['wsOwnerStemLookups'] = stems
            params['attributeAssignType'] = 'stem'
        elif groups is not None:
            groups = [str_to_group(group) for group in groups]
            params['wsOwnerGroupLookups'] = [group.get_group_lookup() for group in groups]
            params['attributeAssignType'] = 'group'

        data['WsRestGetAttributeAssignmentsRequest'].update(params)

        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response
