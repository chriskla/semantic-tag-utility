"""
    This module provides utility functions to convert an Abstract Syntax Tree (AST) 
    representation of entities into JSON-LD format.
    Functions:
        _merge(d1, d2):
            Recursively merges two dictionaries. If both dictionaries have a key 
            with a dictionary as a value, the function merges those dictionaries 
            as well. Otherwise, it prioritizes the value from the first dictionary 
            if it exists, or the second dictionary otherwise.
        _get_context_for_type(type, metadata_dir):
            Retrieves the JSON-LD context for a given type from a specified 
            metadata directory.
        ast_to_jsonld(input_file, output_file, base_uri, metadata_dir):
            Converts a JSON file containing AST entities into a JSON-LD file. 
            Each entity is enriched with its context and a base URI.
    _summary_
"""

import json
def _merge(d1, d2):
    merged_dict = {}
    for key in set(d1.keys()) | set(d2.keys()):
        value_d1 = d1.get(key, None)
        value_d2 = d2.get(key, None)

        if isinstance(value_d1, dict) and isinstance(value_d2, dict):
            merged_dict[key] = _merge(value_d1, value_d2)
        elif value_d1 is not None:
            merged_dict[key] = value_d1
        else:
            assert value_d2 is not None
            merged_dict[key] = value_d2

    return merged_dict


def _get_context_for_type(type, metadata_dir):
    with open(f"{metadata_dir}/{type}.jsonld", "r") as context_file:
        context = json.load(context_file)
        return context


def ast_to_jsonld(input_file, output_file, base_uri, metadata_dir):
    converted_entities = []
    with open(input_file, "r") as model_ast_file:
        model_entities = json.load(model_ast_file)
        for entity in model_entities:
            payload = entity["payload"]
            identity = entity["identity"]
            entry = _merge(payload, identity)
            entry = _merge(entry, _get_context_for_type(payload["@type"], metadata_dir))
            entry["@context"]["@base"] = base_uri
            converted_entities.append(entry)

    with open(output_file, "w") as export_file:
        json.dump(converted_entities, export_file, indent=4)
