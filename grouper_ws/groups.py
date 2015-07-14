from __future__ import absolute_import

import base64
from datetime import datetime
import json

try: # Py3
    from urllib.parse import quote, urljoin
except ImportError: # Py2
    from urlparse import urljoin
    from urllib import quote

from .subjects import Subject


class Group(object):
    def __init__(self, group_name, display_name=None, uuid=None,
                 created_time=None, modified_time=None,
                 *args, **kwargs):
        self.group_name = group_name
        self.extension = group_name.split(':')[-1]
        self.display_name = self.extension
        if display_name is not None:
            self.display_name = display_name
        self.group_type = "group"
        self.uuid = uuid
        self._created_time = created_time
        self._modified_time = modified_time

    def get_details(self):
        return {
            'hasComposite': 'F',
        }

    def is_composite(self):
        return False

    def created(self):
        if self._created_time is None:
            return datetime.min
        return datetime.strptime(self._details['createTime'], '%Y/%m/%d %H:%M:%S.%f')

    def modified(self):
        if self._modified_time is None:
            return datetime.min
        return datetime.strptime(self._details['modifyTime'], '%Y/%m/%d %H:%M:%S.%f')

    def to_json_dict(self, include_details=True):
        wsGroup = {
            'name': self.group_name,
            'displayExtension': self.display_name,
        }
        if include_details:
            wsGroup['detail'] = self.get_details()
        return {
            'wsGroup': wsGroup,
            'wsGroupLookup': self.get_group_lookup(),
            'createParentStemsIfNotExist': 'T',
        }

    def get_group_lookup(self):
        return {
            'groupName': self.group_name,
        }

    def __str__(self):
        return "Group: %s" % self.group_name

    def get_subject(self):
        if self.uuid is not None:
            return Subject(source_id="g:gsa", subject_id=self.uuid)
        return Subject(source_id="g:gsa", subject_identifier=self.group_name)


class CompositeGroup(Group):
    COMPOSITE_TYPES = ['union', 'intersection', 'complement']

    def __init__(self, group_name, left_group=None, right_group=None,
                 composite_type='intersection', *args, **kwargs):
        super(CompositeGroup, self).__init__(group_name, *args, **kwargs)
        composite_type = composite_type.lower()
        if composite_type not in CompositeGroup.COMPOSITE_TYPES:
            raise Exception("Unknown composite type '%s'" % (composite_type))
        if not isinstance(left_group, Group):
            left_group = Group(left_group)
        if not isinstance(right_group, Group):
            right_group = Group(right_group)
        self.left_group = left_group
        self.right_group = right_group
        self.composite_type = composite_type

    def is_composite(self):
        return True

    def get_details(self):
        details = super(CompositeGroup, self).get_details()
        details.update({
            'hasComposite': 'T',
            'leftGroup': self.left_group.to_json_dict(False)['wsGroup'],
            'rightGroup': self.right_group.to_json_dict(False)['wsGroup'],
            'compositeType': self.composite_type,
        })
        return details

    def __str__(self):
        return "Composite group: %s (%s [%s] %s)" % (
            self.group_name, self.left_group, self.composite_type, self.right_group
        )


def group_from_json_dict(json_dict):
    # Extract wsGroup if present, otherwise assume we have group data
    json_dict = json_dict.get('wsGroup', json_dict)
    group_name = json_dict['name']
    details = json_dict.get('detail', {})
    uuid = json_dict.get('uuid', None)
    created = details.get('createTime', None)
    modified = details.get('modifyTime', None)
    group = Group(
        group_name,
        uuid=uuid,
        created_time=created,
        modified_time=modified
    )

    composite = details.get('hasComposite', 'F')
    if composite == 'T':
        # Extract left/right group
        left_group = group_from_json_dict(details.get('leftGroup', {}))
        right_group = group_from_json_dict(details.get('rightGroup', {}))
        composite_type = details.get('compositeType', None)
        group = CompositeGroup(
            group_name,
            left_group,
            right_group,
            composite_type, 
            uuid=uuid,
            created_time=created,
            modified_time=modified
        )
    return group
