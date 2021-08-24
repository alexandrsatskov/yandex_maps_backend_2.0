from inspect import getdoc
from itertools import count
from typing import Type
from pydantic import BaseModel
from aiohttp_pydantic.oas.struct import OpenApiSpec3, OperationObject, PathItem
from aiohttp_pydantic.oas.view import (
    PydanticView, _parse_func_signature,
    docstring_parser, _handle_optional,
    _OASResponseBuilder
)


def _add_http_method_to_oas(
    oas: OpenApiSpec3, oas_path: PathItem, http_method: str, view: Type[PydanticView]
):
    http_method = http_method.lower()
    oas_operation: OperationObject = getattr(oas_path, http_method)
    handler = getattr(view, http_method)
    path_args, body_args, qs_args, header_args, defaults = _parse_func_signature(
        handler
    )
    description = getdoc(handler)
    if description:
        oas_operation.description = docstring_parser.operation(description)
        status_code_descriptions = docstring_parser.status_code(description)
    else:
        status_code_descriptions = {}

    if body_args:
        body_schema = (
            next(iter(body_args.values()))
                .schema(ref_template="#/components/schemas/{model}")
                .copy()
        )
        if def_sub_schemas := body_schema.pop("definitions", None):
            oas.components.schemas.update(def_sub_schemas)

        oas_operation.request_body.content = {
            "application/json": {"schema": body_schema}
        }

    indexes = count()
    for args_location, args in (
        ("path", path_args.items()),
        ("query", qs_args.items()),
        ("header", header_args.items()),
    ):
        for name, type_ in args:
            i = next(indexes)
            oas_operation.parameters[i].in_ = args_location
            oas_operation.parameters[i].name = name
            optional_type = _handle_optional(type_)

            # START: monkey-patch here
            from enum import EnumMeta
            from pydantic.schema import enum_process_schema
            if isinstance(optional_type, EnumMeta):
                enum_schema = enum_process_schema(optional_type)
                oas.components.schemas.update({f"{enum_schema['title']}": enum_schema})
            # END:

            attrs = {"__annotations__": {"__root__": type_}}
            if name in defaults:
                attrs["__root__"] = defaults[name]

            oas_operation.parameters[i].schema = type(name, (BaseModel,), attrs).schema(
                ref_template="#/components/schemas/{model}"
            )

            oas_operation.parameters[i].required = optional_type is None

    return_type = handler.__annotations__.get("return")
    if return_type is not None:
        _OASResponseBuilder(oas, oas_operation, status_code_descriptions).build(
            return_type
        )
