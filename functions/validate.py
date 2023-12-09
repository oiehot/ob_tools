import re
from dataclasses import dataclass
from enum import Enum

import bpy

OBJECT_NAME_RE = re.compile(r"^[A-Z][a-zA-Z0-9._]*$")
COLLECTION_NAME_RE = re.compile(r"^[A-Z][.a-zA-Z0-9._]*$")
MATERIAL_NAME_RE = re.compile(r"^M_[A-Z][.a-zA-Z0-9._]*$")


class IssueLevel(Enum):
    Info = 1
    Error = 2
    Warning = 3


@dataclass
class Issue:
    level: IssueLevel
    node_name: str
    node_type: str
    message: str


def is_many_dot(text: str) -> bool:
    return True if text.count('.') >= 2 else False


def is_valid_object_name(name: str) -> bool:
    if is_many_dot(name):
        return False
    if not OBJECT_NAME_RE.match(name):
        return False
    return True


def is_valid_collection_name(name: str) -> bool:
    if is_many_dot(name):
        return False
    if not COLLECTION_NAME_RE.match(name):
        return False
    return True


def is_valid_material_name(name: str) -> bool:
    if is_many_dot(name):
        return False
    if not MATERIAL_NAME_RE.match(name):
        return False
    return True


def get_objects_issues() -> list[Issue]:
    issues: list[Issue] = []
    for obj in bpy.data.objects:
        if not is_valid_object_name(obj.name):
            issue = Issue(
                level=IssueLevel.Warning,
                node_name=obj.name, node_type="Object",
                message="Invalid Object Name"
            )
            issues.append(issue)
    return issues


def get_collection_issues() -> list[Issue]:
    issues: list[Issue] = []
    for collection in bpy.data.collections:
        if not is_valid_collection_name(collection.name):
            issue = Issue(
                level=IssueLevel.Warning,
                node_name=collection.name, node_type="Collection",
                message="Invalid Collection Name"
            )
            issues.append(issue)
    return issues


def get_material_issues() -> list[Issue]:
    issues: list[Issue] = []
    for material in bpy.data.materials:
        if not is_valid_material_name(material.name):
            issue = Issue(
                level=IssueLevel.Warning,
                node_name=material.name, node_type="Material",
                message="Invalid Material Name"
            )
            issues.append(issue)
    return issues


def print_issues(issues: list[Issue]) -> None:
    for issue in issues:
        level_str: str = (str(issue.level)).split(".")[1].upper()
        print(f"[{level_str}] {issue.node_name} ({issue.node_type}): {issue.message}")
