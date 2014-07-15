import base64
import json
import requests
import logging
from requests_negotiate import HTTPNegotiateAuth
from urlparse import urljoin
from urllib import quote
from queries import *
from groups import *


DEFAULT_SUBJECT_ATTRIBUTES = [
    "description",
    "oakpersonid",
    "oakoxfordssousername",
    "name"
]

logger = logging.getLogger(__name__)


class Grouper(object):
    def __init__(self, host_name, base_url, auth=HTTPNegotiateAuth()):
        self.host_name = host_name
        self.base_url = urljoin('https://' + self.host_name, base_url)
        self.username = "cud/arbitrary.it.ox.ac.uk@OX.AC.UK"
        self.auth = auth

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

    def add_members(self, group, members):
        url = 'servicesRest/v2_1_005/groups/{0}/members'.format(quote(group))
        members_list = [{
            'subjectId': member,

            # Skip lookup of Kerberos credentials
            'subjectSourceId': 'OAK',
        } for member in members]

        data = {
            'WsRestAddMemberRequest': {
                'actAsSubjectLookup': {'subjectId': self.username},
                'replaceAllExisting': 'F',
                'subjectLookups': members_list,
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(requests.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def find_groups(self, query):
        url = 'servicesRest/v2_1_005/groups/'

        data = {
            'WsRestFindGroupsRequest': {
                'actAsSubjectLookup': {'subjectId': self.username},
                'wsQueryFilter': query.to_json_dict(),
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(requests.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def lookup_groups(self, groups):
        url = 'servicesRest/v2_1_005/groups/'
        group_list = [{'groupName': group} for group in groups]

        data = {
            'WsRestFindGroupsRequest': {
                'actAsSubjectLookup': {'subjectId': self.username},
                'wsGroupLookups': group_list,
                'includeGroupDetail': 'T',
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(requests.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def has_members(self, group, members):
        url = 'servicesRest/v2_1_005/groups/{0}/members'.format(quote(group))
        members_list = [{
            'subjectId': member,

            # Skip lookup of Kerberos credentials
            'subjectSourceId': 'OAK',
        } for member in members]

        data = {
            'WsRestHasMemberRequest': {
                'actAsSubjectLookup': {'subjectId': self.username},
                'subjectLookups': members_list,
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(requests.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_members(self, groups, subject_attributes=DEFAULT_SUBJECT_ATTRIBUTES):
        url = 'servicesRest/v2_1_005/groups'
        group_list = [{'groupName': group} for group in groups]

        data = {
            'WsRestGetMembersRequest': {
                'actAsSubjectLookup': {'subjectId': self.username},
                'subjectAttributeNames': subject_attributes,
                'wsGroupLookups': group_list,
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(requests.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def get_group_memberships(self, group, member_filter='All', subject_attributes=DEFAULT_SUBJECT_ATTRIBUTES):
        url = 'servicesRest/v2_1_005/groups/{0}/memberships'.format(quote(group))
        member_filter_values = ['All', 'Effective', 'Immediate', 'Composite', 'NonImmediate']
        if member_filter not in member_filter_values:
            raise Exception("member_filter must be in '{0}'".format(member_filter_values))

        data = {
            'WsRestGetMembershipsRequest': {
                'actAsSubjectLookup': {'subjectId': self.username},
                'subjectAttributeNames': subject_attributes,
                #'memberFilter': 'All',
                'includeGroupDetail': 'T',
                'includeSubjectDetail': 'T',
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(requests.post, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

    def save_groups(self, groups):
        url = 'servicesRest/v2_1_005/groups'

        def str_to_group(group):
            if isinstance(group, Group):
                return group
            else:
                return Group(str(group))

        groups = [str_to_group(group) for group in groups]

        data = {
            'WsRestGroupSaveRequest': {
                'actAsSubjectLookup': {'subjectId': self.username},
                'includeGroupDetail': 'T',
                'wsGroupToSaves': [g.to_json_dict() for g in groups],
            },
        }
        logger.debug(json.dumps(data, indent=2))
        response = self.request(requests.put, url, data)
        logger.debug(json.dumps(response, indent=2))
        return response

