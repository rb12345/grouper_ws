import base64
import json
import requests
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
        print json.dumps(data, indent=2)
        response = self.request(requests.put, url, data)
        print json.dumps(response, indent=2)
        return response

    def find_groups(self, query):
        url = 'servicesRest/v2_1_005/groups/'

        data = {
            'WsRestFindGroupsRequest': {
                'actAsSubjectLookup': {'subjectId': self.username},
                'wsQueryFilter': query.to_json_dict(),
            },
        }
        print json.dumps(data, indent=2)
        response = self.request(requests.post, url, data)
        print json.dumps(response, indent=2)
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
        print json.dumps(data, indent=2)
        response = self.request(requests.post, url, data)
        print json.dumps(response, indent=2)
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
        print json.dumps(data, indent=2)
        response = self.request(requests.put, url, data)
        print json.dumps(response, indent=2)
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
        print json.dumps(data, indent=2)
        response = self.request(requests.post, url, data)
        print json.dumps(response, indent=2)
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
        print json.dumps(data, indent=2)
        response = self.request(requests.post, url, data)
        print json.dumps(response, indent=2)
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
        print json.dumps(data, indent=2)
        response = self.request(requests.put, url, data)
        print json.dumps(response, indent=2)
        return response


if __name__ == '__main__':
    import httplib
    import sys

    try:
        host_name = sys.argv[1]
    except IndexError:
        sys.stderr.write('You must supply a hostname as a first parameter.\n')
        sys.exit(1)
    # '/ws/' is the path on the server where the web services live.
    grouper = Grouper(host_name, '/ws/')

    potential_members = [
    ]
    grouper.add_members('profiling:in-out', potential_members)
