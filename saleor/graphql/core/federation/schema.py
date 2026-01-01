from collections import defaultdict
from typing import Any
import json
import logging
import os
import time

import graphene
from django.conf import settings
from graphene.utils.str_converters import to_snake_case
from graphql import GraphQLArgument, GraphQLError, GraphQLField, GraphQLList

from ...schema_printer import print_schema
from .. import ResolveInfo
from ..context import BaseContext
from .entities import federated_entities

logger = logging.getLogger(__name__)
_SCHEMA_DEBUG = os.getenv("SALEOR_SCHEMA_DEBUG") == "1"

def debug_log(location, message, data=None, hypothesis_id=None):
    """Optional schema debug logger. Emits JSON to standard logs when enabled."""
    if not _SCHEMA_DEBUG:
        return
    payload = {
        "location": location,
        "message": message,
        "timestamp": time.time(),
        "sessionId": "debug-session",
        "runId": "run1",
    }
    if hypothesis_id:
        payload["hypothesisId"] = hypothesis_id
    if data:
        payload["data"] = data
    logger.info("[schema-debug] %s", json.dumps(payload, default=str))


class _Any(graphene.Scalar):
    """_Any value scalar as defined by Federation spec."""

    __typename = graphene.String(required=True)

    @staticmethod
    def serialize(any_value: Any):
        return any_value

    @staticmethod
    def parse_literal(any_value: Any):
        return any_value

    @staticmethod
    def parse_value(any_value: Any):
        return any_value


class _Entity(graphene.Union):
    """_Entity union as defined by Federation spec."""

    class Meta:
        types = tuple(federated_entities.values())


class _Service(graphene.ObjectType):
    """_Service manifest as defined by Federation spec."""

    sdl = graphene.String()


def build_federated_schema(
    query, mutation, types, subscription, directives=None
) -> graphene.Schema:
    """Create GraphQL schema that supports Apollo Federation."""
    # #region agent log
    try:
        types_list = list(types) + [_Any, _Entity, _Service]
        type_names = [getattr(t, "__name__", str(t)) for t in types_list]
        decimal_in_types = [t for t in types_list if getattr(t, "__name__", None) == "Decimal"]
        debug_log("federation/schema.py:50", "About to build federated schema", {
            "typesCount": len(types_list),
            "typeNames": type_names[:20],
            "decimalInTypesCount": len(decimal_in_types),
            "decimalInTypesIds": [id(t) for t in decimal_in_types],
            "decimalInTypesModules": [getattr(t, "__module__", "unknown") for t in decimal_in_types]
        }, hypothesis_id="H1")
    except Exception:
        pass
    # #endregion
    try:
        schema = graphene.Schema(
            query=query,
            mutation=mutation,
            types=list(types) + [_Any, _Entity, _Service],
            subscription=subscription,
            directives=directives,
        )
    except AssertionError as e:
        # #region agent log
        try:
            import traceback
            debug_log("federation/schema.py:57", "AssertionError during schema creation", {
                "error": str(e),
                "errorType": type(e).__name__,
                "traceback": traceback.format_exc()[:500]
            }, hypothesis_id="H1")
        except Exception:
            pass
        # #endregion
        raise
    # #region agent log
    try:
        # Check if Decimal type exists in schema
        decimal_type = schema.get_type("Decimal")
        if decimal_type:
            debug_log("federation/schema.py:57", "Decimal type found in schema after build", {
                "decimalTypeId": id(decimal_type),
                "decimalTypeName": decimal_type.name if hasattr(decimal_type, "name") else "unknown",
                "decimalTypeModule": getattr(decimal_type, "__module__", "unknown")
            }, hypothesis_id="H1")
    except Exception:
        pass
    # #endregion

    entity_type = schema.get_type("_Entity")
    entity_type.resolve_type = create_entity_type_resolver(schema)

    query_type = schema.get_type("Query")
    query_type.fields["_entities"] = GraphQLField(
        GraphQLList(entity_type),
        args={
            "representations": GraphQLArgument(
                GraphQLList(schema.get_type("_Any")),
            ),
        },
        resolver=resolve_entities,
    )
    query_type.fields["_service"] = GraphQLField(
        schema.get_type("_Service"),
        resolver=create_service_sdl_resolver(schema),
    )

    return schema


def create_entity_type_resolver(schema):
    """Create type resolver aware of ChannelContext on _Entity union."""

    def resolve_entity_type(instance, info: ResolveInfo):
        # Use new strategy to resolve GraphQL Type for `ObjectType`
        if isinstance(instance, BaseContext):
            model = type(instance.node)
        else:
            model = type(instance)

        model_type = schema.get_type(model._meta.object_name)
        if model_type is None:
            raise ValueError(
                f"GraphQL type for model {model} could not be found. "
                "This is caused by federated type missing get_model method."
            )

        return model_type

    return resolve_entity_type


def resolve_entities(_, info: ResolveInfo, *, representations):
    max_representations = settings.FEDERATED_QUERY_MAX_ENTITIES
    if max_representations and len(representations) > max_representations:
        representations_count = len(representations)
        raise GraphQLError(
            f"Federated query exceeded entity limit: {representations_count} "
            f"items requested over {max_representations}."
        )

    resolvers = {}
    for representation in representations:
        if representation["__typename"] not in resolvers:
            try:
                model = federated_entities[representation["__typename"]]
                resolvers[representation["__typename"]] = getattr(
                    model,
                    "_{}__resolve_references".format(representation["__typename"]),
                )
            except AttributeError:
                pass

    batches = defaultdict(list)
    for representation in representations:
        model = federated_entities[representation["__typename"]]
        model_arguments = representation.copy()
        typename = model_arguments.pop("__typename")
        model_arguments = {to_snake_case(k): v for k, v in model_arguments.items()}
        model_instance = model(**model_arguments)
        batches[typename].append(model_instance)

    entities = []
    for typename, batch in batches.items():
        if typename not in resolvers:
            continue

        resolver = resolvers[typename]
        entities.extend(resolver(batch, info))

    return entities


def create_service_sdl_resolver(schema):
    # subscriptions are not handled by the federation protocol
    try:
        # Filter out scalar types from schema.types to avoid duplicate registration
        # Scalar types are auto-discovered from fields, so passing them explicitly causes duplicates
        types_to_pass = []
        if hasattr(schema, "types"):
            for t in schema.types:
                # Only pass non-scalar types - scalars are auto-discovered
                if isinstance(t, type):
                    # Check if it's a scalar type class
                    try:
                        if issubclass(t, graphene.Scalar):
                            continue
                    except TypeError:
                        # Some objects can satisfy isinstance(t, type) but still break issubclass.
                        pass
                types_to_pass.append(t)
        else:
            types_to_pass = []
        
        schema_sans_subscriptions = graphene.Schema(
            query=schema._query,
            mutation=schema._mutation,
            types=types_to_pass,  # Only pass non-scalar types
            directives=schema._directives,
        )
    except AssertionError as e:
        raise
    # Render schema to string
    federated_schema_sdl = print_schema(schema_sans_subscriptions)

    del schema_sans_subscriptions

    # Remove "schema { ... }"
    schema_start = federated_schema_sdl.find("schema {")
    schema_end = federated_schema_sdl.find("}", schema_start) + 1
    federated_schema_sdl = (
        federated_schema_sdl[:schema_start] + federated_schema_sdl[schema_end:]
    ).lstrip()

    # Append "@key" to federated types
    for type_name, graphql_type in federated_entities.items():
        type_sdl = f"type {type_name} "
        type_start = federated_schema_sdl.find(type_sdl)
        type_fields_open = federated_schema_sdl.find("{", type_start)
        federated_schema_sdl = (
            federated_schema_sdl[:type_fields_open]
            + getattr(graphql_type, "_sdl")
            + " "
            + federated_schema_sdl[type_fields_open:]
        )

    def resolve_service_sdl(_root, _info: ResolveInfo):
        return {"sdl": federated_schema_sdl}

    return resolve_service_sdl
