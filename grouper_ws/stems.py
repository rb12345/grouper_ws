import base64
import json
from urlparse import urljoin
from urllib import quote
from datetime import datetime


class Stem(object):
    def __init__(self, stem_name, display_name=None, uuid=None, *args, **kwargs):
        super(Stem, self).__init__(*args, **kwargs)
        self.stem_name = stem_name
        self.display_name = stem_name.split(':')[-1]
        if display_name is not None:
            self.display_name = display_name
        self.stem_type = "stem"
        self.__uuid = uuid

    def uuid(self):
        return self.__uuid

    def to_json_dict(self):
        wsStem = {
            'name': self.stem_name,
            'displayExtension': self.display_name,
        }
        return {
            'wsStem': wsStem,
            'wsStemLookup': self.get_stem_lookup(),
            'createParentStemsIfNotExist': 'T',
        }

    def get_stem_lookup(self):
        return {
            'stemName': self.stem_name,
        }

    def __str__(self):
        return "Stem: %s" % self.stem_name


def stem_from_json_dict(json_dict):
    # Extract wsStem if present, otherwise assume we have stem data
    json_dict = json_dict.get('wsStem', json_dict)
    stem_name = json_dict['name']
    display_name = json_dict.get('displayExtension', None)
    uuid = json_dict.get('uuid', None)

    stem = Stem(stem_name, display_name=display_name, uuid=uuid)
    return stem
