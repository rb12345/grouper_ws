import base64
import json
from urlparse import urljoin
from urllib import quote
from datetime import datetime


class Group(object):
    def __init__(self, group_name, details={}, description=None, *args, **kwargs):
        super(Group, self).__init__(*args, **kwargs)
        self.group_name = group_name
        self.description = group_name
        if description is not None:
            self.description = description
        self.group_type = "group"
        self.__details = details

    def get_details(self):
        return {
            'hasComposite': 'F',
        }

    def is_composite(self):
        return False

    def created(self):
        if 'createTime' not in self.__details:
            return datetime.min
        return datetime.strptime(self.__details['createTime'], '%Y/%m/%d %H:%M:%S.%f')

    def modified(self):
        if 'createTime' not in self.__details:
            return datetime.min
        return datetime.strptime(self.__details['createTime'], '%Y/%m/%d %H:%M:%S.%f')

    def to_json_dict(self, include_details=True):
        wsGroup = {
            'name': self.group_name,
            'description': self.description,
        }
        if include_details:
            wsGroup['detail'] = self.get_details()
        return {
            'wsGroup': wsGroup,
            'wsGroupLookup': {
                'groupName': self.group_name,
            }
        }

    def __str__(self):
        return "Group: %s" % self.group_name


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
    group = Group(group_name)

    details = json_dict.get('detail', {})
    composite = details.get('hasComposite', 'F')
    if composite == 'T':
        # Extract left/right group
        left_group = group_from_json_dict(details.get('leftGroup', {}))
        right_group = group_from_json_dict(details.get('rightGroup', {}))
        composite_type = details.get('compositeType', None)
        group = CompositeGroup(group_name, left_group, right_group, composite_type, details=details)
    return group
