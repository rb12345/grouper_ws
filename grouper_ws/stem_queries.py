from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import base64
import json

try: # Py3
    from urllib.parse import quote, urljoin
except ImportError: # Py2
    from urlparse import urljoin
    from urllib import quote

import requests

from .queries import *


AND = 'AND'
FIND_BY_APPROXIMATE_ATTRIBUTE = 'FIND_BY_APPROXIMATE_ATTRIBUTE'
FIND_BY_EXACT_ATTRIBUTE = 'FIND_BY_EXACT_ATTRIBUTE'
FIND_BY_PARENT_STEM_NAME = 'FIND_BY_PARENT_STEM_NAME'
FIND_BY_STEM_NAME_APPROXIMATE = 'FIND_BY_STEM_NAME_APPROXIMATE'
FIND_BY_STEM_NAME= 'FIND_BY_STEM_NAME'
FIND_BY_STEM_UUID = 'FIND_BY_STEM_UUID'
MINUS = 'MINUS'
OR = 'OR'


class StemQueryFilter(object):
    def __init__(self, *args, **kwargs):
        pass

    @property
    def query_type(self):
        return None

    def to_json_dict(self):
        return {
            'stemQueryFilterType': self.query_type,
        }


class FindByParentStemName(StemQueryFilter):
    def __init__(self, parent_stem_name=':', stem_name='', recursive=False, *args, **kwargs):
        super(FindByParentStemName, self).__init__(*args, **kwargs)
        self.stem_name = stem_name
        self.parent_stem_name = parent_stem_name
        self.recursive = recursive

    @property
    def query_type(self):
        return FIND_BY_PARENT_STEM_NAME

    def to_json_dict(self):
        query = super(FindByParentStemName, self).to_json_dict()
        query.update({
            'parentStemName': self.parent_stem_name,
        })
        if self.stem_name is not None:
            query['stemName'] = self.stem_name
        if self.recursive:
            query['parentStemNameScope'] = 'ALL_IN_SUBTREE'
        return query


class FindByStemName(StemQueryFilter):
    def __init__(self, parent_stem_name='', stem_name='', approximate=False, *args, **kwargs):
        super(FindByStemName, self).__init__(*args, **kwargs)
        self.stem_name = stem_name
        self.parent_stem_name = parent_stem_name
        self.approximate = approximate

    @property
    def query_type(self):
        if self.approximate:
            return FIND_BY_STEM_NAME_APPROXIMATE
        return FIND_BY_STEM_NAME

    def to_json_dict(self):
        query = super(FindByStemName, self).to_json_dict()
        if self.approximate:
            query.update({
                'stemName': self.stem_name,
                'parentStemName': self.parent_stem_name,
            })
        else:
            if self.parent_stem_name != '':
                query.update({
                    'stemName': ':'.join([self.parent_stem_name, self.stem_name]),
                })
            else:
                query.update({
                    'stemName': self.stem_name,
                })
        return query


class FindByAttribute(StemQueryFilter):
    def __init__(self, attribute_name, attribute_value, approximate=False, stem_name=None, *args, **kwargs):
        super(FindByAttribute, self).__init__(*args, **kwargs)
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.stem_name = stem_name

    @property
    def query_type(self):
        return FIND_BY_APPROXIMATE_ATTRIBUTE

    def to_json_dict(self):
        query = super(FindByAttribute, self).to_json_dict()
        query.update({
            'stemAttributeName': self.attribute_name,
            'stemAttributeValue': self.attribute_value,
        })
        if self.stem_name is not None:
            query.update({'stemName': self.stem_name})
        return query


class And(StemQueryFilter):
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
            'stemQueryFilter0': self.query1.to_json_dict(),
            'stemQueryFilter1': self.query2.to_json_dict(),
        })
        return query


class Or(StemQueryFilter):
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
            'stemQueryFilter0': self.query1.to_json_dict(),
            'stemQueryFilter1': self.query2.to_json_dict(),
        })
        return query


class Minus(StemQueryFilter):
    def __init__(self, query1, query2, *args, **kwargs):
        super(Minus, self).__init__(*args, **kwargs)
        self.query1 = query1
        self.query2 = query2

    @property
    def query_type(self):
        return MINUS

    def to_json_dict(self):
        query = super(Minus, self).to_json_dict()
        query.update({
            'stemQueryFilter0': self.query1.to_json_dict(),
            'stemQueryFilter1': self.query2.to_json_dict(),
        })
        return query

