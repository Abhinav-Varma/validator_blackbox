"""
All user-land transformation functions.
"""
from typing import Any
from src.custom_types import PathExpr, OpExpr


def path(jsonpath: str) -> PathExpr:
    return PathExpr(jsonpath)


def CAPITALIZE(source) -> OpExpr:
    return OpExpr("capitalize", [source])


def SUBSTR(source, start, length) -> OpExpr:
    return OpExpr("substr", [source, start, length])


def join_parts(*parts: Any) -> OpExpr:
    return OpExpr("join_parts", list(parts))


def GST_DETAILS_ALL(source) -> OpExpr:
    return OpExpr("gst_details_all", [source])
