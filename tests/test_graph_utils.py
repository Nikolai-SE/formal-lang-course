import pytest
import project  # on import will print something from __init__ file
from project.graph_utils import GraphUtils
import filecmp
import os
import shutil


def setup_module(module):
    print("graph_utils setup module")


def teardown_module(module):
    print("graph_utils teardown module")


def test_1_graph_info():
    skos_graph_info = GraphUtils.graph_info_by_name("skos")
    assert skos_graph_info == GraphUtils.GraphInfo(
        number_of_nodes=144,
        number_of_edges=252,
        sorted_labels=[
            "type",
            "definition",
            "isDefinedBy",
            "label",
            "subPropertyOf",
            "comment",
            "scopeNote",
            "inverseOf",
            "range",
            "domain",
            "contributor",
            "disjointWith",
            "creator",
            "example",
            "first",
            "rest",
            "description",
            "seeAlso",
            "subClassOf",
            "title",
            "unionOf",
        ],
    )
    print("skos graph info asserted")

    wc_graph_info = GraphUtils.graph_info_by_name("wc")
    assert wc_graph_info == GraphUtils.GraphInfo(
        number_of_nodes=332, number_of_edges=269, sorted_labels=["d", "a"]
    )
    print("wc graph info asserted")

    generations_graph_info = GraphUtils.graph_info_by_name("generations")
    assert generations_graph_info == GraphUtils.GraphInfo(
        number_of_nodes=129,
        number_of_edges=273,
        sorted_labels=[
            "type",
            "first",
            "rest",
            "onProperty",
            "intersectionOf",
            "equivalentClass",
            "someValuesFrom",
            "hasValue",
            "hasSex",
            "hasChild",
            "hasParent",
            "inverseOf",
            "sameAs",
            "hasSibling",
            "oneOf",
            "range",
            "versionInfo",
        ],
    )
    print("generations graph info asserted")


def test_2_create_two_cycle_labeled_graph_and_save():
    dir_name = "test_2_create_two_cycle_labeled_graph_and_save"
    try:
        os.mkdir(dir_name)
        GraphUtils.create_two_cycle_labeled_graph_and_save(
            10, 20, ("a", "b"), dir_name + "/1.dot"
        )
        GraphUtils.create_two_cycle_labeled_graph_and_save(
            10, 20, ("a", "b"), dir_name + "/2.dot"
        )
        assert filecmp.cmp(dir_name + "/1.dot", dir_name + "/2.dot", shallow=False)
    except Exception as e:
        assert e is None
    finally:
        shutil.rmtree(dir_name)


def test_3_check_correctness_of_graph_file():
    dir_name = "test_3_check_correctness_of_graph_file"
    try:
        os.mkdir(dir_name)
        GraphUtils.create_two_cycle_labeled_graph_and_save(
            4, 5, ("a", "b"), dir_name + "/1.dot"
        )

        with open(dir_name + "/1.dot") as file:
            file_lines = "".join(file.readlines())
            original_graph = """\
digraph  {
1;
2;
3;
4;
0;
5;
6;
7;
8;
9;
1 -> 2  [key=0, label=a];
2 -> 3  [key=0, label=a];
3 -> 4  [key=0, label=a];
4 -> 0  [key=0, label=a];
0 -> 1  [key=0, label=a];
0 -> 5  [key=0, label=b];
5 -> 6  [key=0, label=b];
6 -> 7  [key=0, label=b];
7 -> 8  [key=0, label=b];
8 -> 9  [key=0, label=b];
9 -> 0  [key=0, label=b];
}
"""
            assert original_graph == file_lines
    except Exception as e:
        assert e is None
    finally:
        shutil.rmtree(dir_name)
