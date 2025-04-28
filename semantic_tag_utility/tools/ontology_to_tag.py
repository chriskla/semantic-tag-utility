"""_summary_
    This module provides utility functions to convert an ontology into a tag-based representation.
    Functions:
        _generate_package(package_name, meta_def="", conn_def=""):
            Generates a package definition string with metadata and connection definitions.
        _generate_connection_def(name_space, object_properties, meta_prefix=""):
            Generates connection definitions for object properties in the ontology.
        _generate_metadata_def(name_space, subject_list, meta_prefix=""):
            Generates metadata definitions for subjects in the ontology.
        ontology_to_tag(input_ontology, ontology_prefix, lib_prefix, output_package, package_name):
            Converts an ontology into a tag-based representation and writes it to a file.
            Args:
                input_ontology (str): Path to the input ontology file.
                ontology_prefix (str): Prefix used in the ontology for classes and properties.
                lib_prefix (str): Prefix to be used for generated metadata and connection definitions.
                output_package (str): Path to the output file where the package will be written.
                package_name (str): Name of the package to be generated.
                None

    Returns:
        _type_: _description_
"""

import rdflib
from rdflib.namespace import RDF, RDFS, OWL


def _generate_package(package_name, meta_def="", conn_def=""):
    package = f"package {package_name}" + " {\n"
    package += "\t//  This package was auto-generated\n\n"
    package += meta_def
    package += conn_def
    package += "}"

    return package


def _generate_connection_def(name_space, object_properties, meta_prefix=""):
    conn_def = ""
    for property in object_properties:
        conn_def += f"\t//  {name_space}{property}\n"
        conn_def += (
            f"\tconnection def {meta_prefix}{property.replace(':', '_')}" + " {\n"
        )
        conn_def += "\t\tend sub;\n"
        conn_def += "\t\tend obj;\n"
        conn_def += "\t}\n\n"

    return conn_def


def _generate_metadata_def(name_space, subject_list, meta_prefix=""):
    meta_def = ""
    for subject in subject_list:
        meta_def += f"\t//  {name_space}{subject}\n"
        meta_def += f"\tmetadata def {meta_prefix}{subject.replace(':', '_')};\n\n"

    return meta_def


def ontology_to_tag(
    input_ontology, ontology_prefix, lib_prefix, output_package, package_name
):
    ontology_class = set()
    ontology_property = []

    g = rdflib.Graph()
    g.parse(input_ontology)
    if not ontology_prefix.endswith(":"):
        ontology_prefix += ":"

    for s in g.subjects(unique=True, predicate=RDF.type, object=RDFS.Class):
        s_name = str(s.n3(g.namespace_manager))
        ontology_class.add(s_name.removeprefix(ontology_prefix))

    for s in g.subjects(unique=True, predicate=RDF.type, object=OWL.Class):
        s_name = str(s.n3(g.namespace_manager))
        ontology_class.add(s_name.removeprefix(ontology_prefix))

    for s in g.subjects(unique=True, predicate=RDF.type, object=OWL.ObjectProperty):
        s_name = str(s.n3(g.namespace_manager))
        ontology_property.append(s_name.removeprefix(ontology_prefix))

    meta_def = _generate_metadata_def(input_ontology, ontology_class, lib_prefix)
    conn_def = _generate_connection_def(input_ontology, ontology_property, lib_prefix)

    with open(output_package, "w") as f:
        f.write(_generate_package(package_name, meta_def, conn_def))
