import base64
import json
from urlparse import urljoin
from urllib import quote
from datetime import datetime


class Subject(object):
    def __init__(self, subject_id=None, source_id=None,
                 subject_identifier=None):
        if subject_id is None and subject_identifier is None:
            raise Exception("No means of identifying subject")
        self.subject_id = subject_id
        self.subject_identifier = subject_identifier
        self.source_id = source_id

    def to_json_dict(self, include_details=True):
        return {
            'wsSubject': {
                'id': self.subject_id,
                'sourceId': self.source_id,
            }
        }

    def get_subject_lookup(self):
        lookup = {}
        if self.subject_id is not None:
            lookup['subjectId'] = self.subject_id
        elif self.subject_identifier is not None:
            lookup['subjectIdentifier'] = self.subject_identifier
        if self.source_id is not None:
            lookup['subjectSourceId'] = self.subject_id
        return lookup

    def __str__(self):
        return "Subject: %s (%s)" % (self.subject_id, self.source_id)

    @staticmethod
    def from_json_dict(json_dict):
        # Extract wsSubjectLookup if present, otherwise assume we have group data
        json_dict = json_dict.get('wsSubjectLookup', json_dict)

        subject_id = json_dict['subjectId']
        source_id = json_dict['subjectSourceId']

        return Subject(subject_id=subject_id, source_id=source_id)
