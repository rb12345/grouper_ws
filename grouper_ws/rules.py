import base64
import json
import logging
from urlparse import urljoin
from urllib import quote
from datetime import datetime
from stems import *
from subjects import Subject


RULES_ATTRIBUTE_BASE = "etc:attribute:rules"
RULES_ATTRIBUTE_RULE = RULES_ATTRIBUTE_BASE + ":rule"
RULES_ATTRIBUTE_ACT_AS_SOURCE = RULES_ATTRIBUTE_BASE + ":ruleActAsSubjectSourceId"
RULES_ATTRIBUTE_ACT_AS_SUBJECT = RULES_ATTRIBUTE_BASE + ":ruleActAsSubjectId"
RULES_ATTRIBUTE_CHECK_TYPE = RULES_ATTRIBUTE_BASE + ":ruleCheckType"
RULES_ATTRIBUTE_CHECK_OWNER_NAME = RULES_ATTRIBUTE_BASE + ":ruleCheckOwnerName"
RULES_ATTRIBUTE_CHECK_SCOPE = RULES_ATTRIBUTE_BASE + ":ruleCheckStemScope"
RULES_ATTRIBUTE_IF = RULES_ATTRIBUTE_BASE + ":ruleIfConditionEnum"
RULES_ATTRIBUTE_IF_ARG0 = RULES_ATTRIBUTE_BASE + ":ruleIfConditionEnumArg0"
RULES_ATTRIBUTE_IF_ARG1 = RULES_ATTRIBUTE_BASE + ":ruleIfConditionEnumArg1"
RULES_ATTRIBUTE_IF_ARG2 = RULES_ATTRIBUTE_BASE + ":ruleIfConditionEnumArg2"
RULES_ATTRIBUTE_THEN = RULES_ATTRIBUTE_BASE + ":ruleThenEnum"
RULES_ATTRIBUTE_THEN_ARG0 = RULES_ATTRIBUTE_BASE + ":ruleThenEnumArg0"
RULES_ATTRIBUTE_THEN_ARG1 = RULES_ATTRIBUTE_BASE + ":ruleThenEnumArg1"
RULES_ATTRIBUTE_THEN_ARG2 = RULES_ATTRIBUTE_BASE + ":ruleThenEnumArg2"
RULES_ATTRIBUTE_IS_VALID = RULES_ATTRIBUTE_BASE + ":ruleValid"

RULES_CHECK_TYPES = [
    "permissionDisabledDate",
    "membershipDisabledDate",
    "flattenedMembershipAddInFolder",
    "flattenedMembershipRemoveInFolder",
    "flattenedMembershipRemove",
    "membershipRemove",
    "membershipRemoveInFolder",
    "groupCreate",
    "stemCreate",
    "membershipAdd",
    "subjectAssignInStem",
    "flattenedMembershipAdd",
    "membershipAddInFolder",
    "attributeDefCreate",
    "permissionAssignToSubject",
]

RULES_IF = [
    "noGroupInFolderHasImmediateEnabledMembership",
    "nameMatchesSqlLikeString",
    "thisGroupAndNotFolderHasImmediateEnabledMembership",
    "thisPermissionDefHasAssignmentAndNotFolder",
    "groupHasNoImmediateEnabledMembership",
    "thisGroupHasImmediateEnabledMembership",
    "thisGroupHasImmediateEnabledNoEndDateMembership",
    "thisPermissionDefHasAssignment",
    "thisPermissionDefHasNoEndDateAssignment",
    "groupHasNoEnabledMembership",
    "never",
]


logger = logging.getLogger(__name__)


def define_rule(grouper, stem, act_as = Subject(source_id="g:isa", subject_id="GrouperSystem"), rule_config={}):
    # Make sure rule check type is valid
    check_type = rule_config.get(RULES_ATTRIBUTE_CHECK_TYPE, None)
    if check_type not in RULES_CHECK_TYPES:
        raise Exception("Invalid rule check type: {0}".format(check_type))

    # Make sure rule if enum type is valid
    if RULES_ATTRIBUTE_IF in rule_config:
        if_enum = rule_config[RULES_ATTRIBUTE_IF]
        if if_enum not in RULES_IF:
            raise Exception("Invalid rule If enum: {0}".format(if_enum))

    r = grouper.assign_attributes(
        stems=[stem],
        attributes=[RULES_ATTRIBUTE_RULE],
        attr_op='add_attr'
    )
    assignment = r['WsAssignAttributesResults']['wsAttributeAssignResults'][0]['wsAttributeAssigns'][0]
    rule_uuid = assignment['id']

    rule_config.update({
        RULES_ATTRIBUTE_ACT_AS_SOURCE: act_as.source_id,
        RULES_ATTRIBUTE_ACT_AS_SUBJECT: act_as.subject_id,
    })

    for attr in rule_config:
        attr_value = rule_config[attr]
        r = grouper.assign_attributes(
            attribute_assigns=[rule_uuid],
            attributes={attr: attr_value},
            attr_value_op='replace_values'
        )

    r_valid = grouper.get_attribute_assignments([stem], RULES_ATTRIBUTE_RULE)

    assignments = r_valid['WsGetAttributeAssignmentsResults']['wsAttributeAssigns']
    logger.debug(assignments)

    rule_valid = [attr for attr in assignments if attr['attributeDefNameName'] == RULES_ATTRIBUTE_IS_VALID]
    is_valid = rule_valid[0]['wsAttributeAssignValues'][0]['valueSystem']
    if is_valid != "T":
        raise Exception(is_valid)

    return rule_uuid


def subject_to_string(subject):
    if not isinstance(subject, Subject):
        raise "subject is not a Subject"

    if subject.subject_id:
        return "{0} :::: {1}".format(subject.source_id, subject.subject_id)
    return "{0} :::::: {1}".format(subject.source_id, subject.subject_identifier)


def inherit_group_privileges(stem, subject, privileges=[], stem_scope="SUB", filter_string=""):
    """
    inherit_group_privileges(stem, subject, privileges=[], stem_scope="SUB", filter_string="")

    Groups created within the specified stem have the specified privileges automatically assigned to the specified
    subject.
    """

    valid_privileges = set(["read", "admin", "update", "view", "optin", "optout"])
    privileges = set(privileges) & valid_privileges

    rule_config = {
        RULES_ATTRIBUTE_CHECK_OWNER_NAME: stem,
        RULES_ATTRIBUTE_CHECK_TYPE: 'groupCreate',
        RULES_ATTRIBUTE_CHECK_SCOPE: stem_scope,
        RULES_ATTRIBUTE_THEN: 'assignGroupPrivilegeToGroupId',
        RULES_ATTRIBUTE_THEN_ARG0: subject_to_string(subject),
        RULES_ATTRIBUTE_THEN_ARG1: ', '.join(privileges),
    }

    return rule_config
