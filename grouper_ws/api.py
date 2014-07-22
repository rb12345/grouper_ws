import base64
import json
import requests
import logging
from requests_negotiate import HTTPNegotiateAuth
from urlparse import urljoin
from urllib import quote
from queries import *
from groups import *
from stems import *


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
    if type(member) == str or type(member) == unicode:
        return {
        'subjectId': member,
        }
    elif type(member) == tuple:
        return {
            'subjectId': member[0],
            'subjectSourceId': member[1],
        }
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
    def __init__(self, host_name, base_url, auth=HTTPNegotiateAuth()):
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
        return http_response.json()

    def add_members(self, group, members, replace_existing=False):
        url = 'servicesRest/v2_1_005/groups/{0}/members'.format(quote(group))

        members_list = [member_to_subject_lookup(member) for member in members]

        data = {
            'WsRestAddMemberRequest': {
                'actAsSubjectLookup': {'subjectId': self.auth.username},
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
                'actAsSubjectLookup': {'subjectId': self.auth.username},
                'wsQueryFilter': query.to_json_dict(),
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
                'actAsSubjectLookup': {'subjectId': self.auth.username},
                'wsGroupLookups': group_list,
                'includeGroupDetail': 'T',
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def has_members(self, group, members):
        url = 'servicesRest/v2_1_005/groups/{0}/members'.format(quote(group))

        members_list = [member_to_subject_lookup(member) for member in members]

        data = {
            'WsRestHasMemberRequest': {
                'actAsSubjectLookup': {'subjectId': self.auth.username},
                'subjectLookups': members_list,
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_members(self, groups, subject_attributes=DEFAULT_SUBJECT_ATTRIBUTES):
        url = 'servicesRest/v2_1_005/groups'
        group_list = [{'groupName': group} for group in groups]

        data = {
            'WsRestGetMembersRequest': {
                'actAsSubjectLookup': {'subjectId': self.auth.username},
                'subjectAttributeNames': subject_attributes,
                'wsGroupLookups': group_list,
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_group_memberships(self, group, member_filter='All', subject_attributes=DEFAULT_SUBJECT_ATTRIBUTES):
        url = 'servicesRest/v2_1_005/groups/{0}/memberships'.format(quote(group))
        member_filter_values = ['All', 'Effective', 'Immediate', 'Composite', 'NonImmediate']
        if member_filter not in member_filter_values:
            raise Exception("member_filter must be in '{0}'".format(member_filter_values))

        data = {
            'WsRestGetMembershipsRequest': {
                'actAsSubjectLookup': {'subjectId': self.auth.username},
                'subjectAttributeNames': subject_attributes,
                'memberFilter': 'All',
                'includeGroupDetail': 'T',
                'includeSubjectDetail': 'T',
            },
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
                'actAsSubjectLookup': {'subjectId': self.auth.username},
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
                'actAsSubjectLookup': {'subjectId': self.auth.username},
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
                'actAsSubjectLookup': {'subjectId': self.auth.username},
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
                'actAsSubjectLookup': {'subjectId': self.auth.username},
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
                'actAsSubjectId': self.auth.username,
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

    def assign_privileges(self, privilege_type, privilege_names,
                          stems=None, groups=None, members=None):
        url = 'servicesRest/v2_1_005/grouperPrivileges'

        data = {
            'WsRestAssignGrouperPrivilegesRequest': {
                'actAsSubjectLookup': {'subjectId': self.auth.username},
                'includeGroupDetail': 'T',
                'includeSubjectDetail': 'T',
            },
        }
        params = {}

        if members is not None:
            members_list = [member_to_subject_lookup(member) for member in members]
            params['wsSubjectLookups'] = members_list
        
        if stems is not None:
            params['wsStemLookups'] = [s.get_stem_lookup() for s in stems]

        if groups is not None:
            params['wsGroupLookups'] = [g.get_group_lookup() for g in groups]

        if members is None and stems is None and groups is None:
            raise Exception("assign_privileges(): No stem, group or subject specified!")

        params['privilegeNames'] = privilege_names
        params['privilegeType'] = privilege_type

        data['WsRestAssignGrouperPrivilegesRequest'].update(params)

        logger.debug(json.dumps(data, indent=2))
        response = self.request(self._session.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response
