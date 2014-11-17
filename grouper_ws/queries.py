#!/usr/bin/env python

import base64
import json
import requests
from urlparse import urljoin
from urllib import quote


AND = 'AND'
FIND_BY_APPROXIMATE_ATTRIBUTE = 'FIND_BY_APPROXIMATE_ATTRIBUTE'
FIND_BY_EXACT_ATTRIBUTE = 'FIND_BY_EXACT_ATTRIBUTE'
FIND_BY_GROUP_NAME_APPROXIMATE = 'FIND_BY_GROUP_NAME_APPROXIMATE'
FIND_BY_GROUP_NAME_EXACT= 'FIND_BY_GROUP_NAME_EXACT'
FIND_BY_GROUP_UUID = 'FIND_BY_GROUP_UUID'
FIND_BY_STEM_NAME = 'FIND_BY_STEM_NAME'
FIND_BY_TYPE = 'FIND_BY_TYPE'
MINUS = 'MINUS'
OR = 'OR'


class QueryFilter(object):
    def __init__(self, *args, **kwargs):
        pass

    @property
    def query_type(self):
        return None

    def to_json_dict(self):
        return {
            'queryFilterType': self.query_type,
        }


class FindByStemName(QueryFilter):
    def __init__(self, stem_name='', *args, **kwargs):
        super(FindByStemName, self).__init__(*args, **kwargs)
        self.stem_name = stem_name

    @property
    def query_type(self):
        return FIND_BY_STEM_NAME

    def to_json_dict(self):
        query = super(FindByStemName, self).to_json_dict()
        query.update({
            'stemName': self.stem_name
        })
        return query


class FindByGroupName(QueryFilter):
    def __init__(self, stem_name='', group_name='', approximate=False, *args, **kwargs):
        super(FindByGroupName, self).__init__(*args, **kwargs)
        self.stem_name = stem_name
        self.group_name = group_name
        self.approximate = approximate

    @property
    def query_type(self):
        if self.approximate:
            return FIND_BY_GROUP_NAME_APPROXIMATE
        return FIND_BY_GROUP_NAME_EXACT

    def to_json_dict(self):
        query = super(FindByGroupName, self).to_json_dict()
        if self.approximate:
            query.update({
                'stemName': self.stem_name,
                'groupName': self.group_name,
            })
        else:
            query.update({
                'groupName': ':'.join([self.stem_name, self.group_name]),
            })
        return query


class FindByType(QueryFilter):
    def __init__(self, group_type, *args, **kwargs):
        super(FindByType, self).__init__(*args, **kwargs)
        self.group_type = group_type

    @property
    def query_type(self):
        return FIND_BY_TYPE

    def to_json_dict(self):
        query = super(FindByType, self).to_json_dict()
        query.update({
            'groupTypeName': self.group_type,
        })
        return query


class FindByAttribute(QueryFilter):
    def __init__(self, attribute_name, attribute_value, approximate=False, stem_name=None, *args, **kwargs):
        super(FindByAttribute, self).__init__(*args, **kwargs)
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.stem_name = stem_name
        self.approximate = approximate

    @property
    def query_type(self):
        if self.approximate:
            return FIND_BY_APPROXIMATE_ATTRIBUTE
        return FIND_BY_EXACT_ATTRIBUTE

    def to_json_dict(self):
        query = super(FindByAttribute, self).to_json_dict()
        query.update({
            'groupAttributeName': self.attribute_name,
            'groupAttributeValue': self.attribute_value,
        })
        if self.stem_name is not None:
            query.update({'stemName': self.stem_name})
        return query


class And(QueryFilter):
    def __init__(self, query1, query2, *args, **kwargs):
        super(And, self).__init__(*args, **kwargs)
        self.query1 = query1
        self.query2 = query2

    @property
    def query_type(self):
        return AND

    def to_json_dict(self):
        query = super(And, self).to_json_dict()
        query.update({
            'queryFilter0': self.query1.to_json_dict(),
            'queryFilter1': self.query2.to_json_dict(),
        })
        return query


class Or(QueryFilter):
    def __init__(self, query1, query2, *args, **kwargs):
        super(Or, self).__init__(*args, **kwargs)
        self.query1 = query1
        self.query2 = query2

    @property
    def query_type(self):
        return OR

    def to_json_dict(self):
        query = super(Or, self).to_json_dict()
        query.update({
            'queryFilter0': self.query1.to_json_dict(),
            'queryFilter1': self.query2.to_json_dict(),
        })
        return query



