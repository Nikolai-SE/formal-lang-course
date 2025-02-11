from pathlib import Path
from networkx import MultiDiGraph
from pyformlang.cfg import CFG
from pyformlang.cfg import Variable
from scipy.sparse import dok_array, eye

from project.grammar import cfg_from_file, cfg_to_weak_cnf
from project.graph_utils import GraphUtils


def matrix_algorithm(
    cfg: CFG, graph: MultiDiGraph
) -> set[tuple[object, Variable, object]]:
    """
    Context free path querying by Matrix algorithm with context free grammar and graph
    @param cfg: context free grammar
    @param graph: graph for querying
    @return: set of (Node, Variable, Node)
    """
    wcnf = cfg_to_weak_cnf(cfg)

    eps_productions = set()
    terminal_productions: dict[object, set[Variable]] = {}
    non_terminal_productions: dict[Variable, set[tuple]] = {}
    for p in wcnf.productions:
        body = p.body
        if len(body) == 0:
            eps_productions.add(p.head)
        elif len(body) == 1:
            terminal_productions.setdefault(body[0].value, set()).add(p.head)
        elif len(body) == 2:
            u, v = body
            non_terminal_productions.setdefault(p.head, set()).add((u, v))
        else:
            raise RuntimeError("matrix_algorithm: Mismatch production")

    nodes_by_index = {i: n for i, n in enumerate(graph.nodes)}
    nodes_indexes = {n: i for i, n in nodes_by_index.items()}
    n = len(nodes_indexes)

    # матрица n × n, в которой каждый элемент ∅
    matrix: dict[Variable, dok_array] = dict()
    for variable in wcnf.variables:
        matrix[variable] = dok_array((n, n), dtype=bool)

    # Инициализация матрицы
    for A, B, label in graph.edges.data("label"):
        for variable in terminal_productions.setdefault(label, set()):
            matrix[variable][nodes_indexes[A], nodes_indexes[B]] = True

    # Добавление петель для нетерминалов, порождающих пустую строку
    for variable in eps_productions:
        matrix[variable] += dok_array((eye(n, dtype=bool)))

    # Вычисление транзитивного замыкания
    isUpdated = True
    while isUpdated:
        isUpdated = False
        for C, AB in non_terminal_productions.items():
            non_zero = matrix[C].count_nonzero()
            for a, b in AB:
                matrix[C] += matrix[a].tocsr().dot(matrix[b].tocsc())
            isUpdated |= matrix[C].count_nonzero() != non_zero

    res = set()
    for variable, matr in matrix.items():
        nz = matr.nonzero()
        for i, j in list(zip(nz[0], nz[1])):
            res.add((nodes_by_index[i], variable, nodes_by_index[j]))
    return res


def matrix_algorithm_graph_from_file(
    graph_filename: Path, cfg: CFG
) -> set[tuple[object, Variable, object]]:
    """
    Context free path querying by Matrix algorithm with context free grammar and graph
    @param graph_filename: context free grammar filename
    @param cfg: graph for querying
    @return: set of (Node, Variable, Node)
    """
    return matrix_algorithm(cfg, GraphUtils.open_graph(graph_filename))


def matrix_algorithm_cfg_from_text(
    graph: MultiDiGraph, cfg_text: str, start_symbol=Variable("S")
) -> set[tuple[object, Variable, object]]:
    """
    Context free path querying by Matrix algorithm with context free grammar and graph
    @param graph: graph for querying
    @param cfg_text: text view of context free grammar
    @param start_symbol: start symbol of grammar
    @return: set of (Node, Variable, Node)
    """
    return matrix_algorithm(CFG.from_text(cfg_text, start_symbol=start_symbol), graph)


def matrix_algorithm_cfg_from_file(
    graph: MultiDiGraph, cfg_filename: str, start_symbol="S"
) -> set[tuple[object, Variable, object]]:
    """
    Context free path querying by Matrix algorithm with context free grammar and graph
    @param graph: graph for querying
    @param cfg_filename: context free grammar filename
    @param start_symbol: start symbol of grammar
    @return: set of (Node, Variable, Node)
    """
    return matrix_algorithm(cfg_from_file(cfg_filename, start_symbol), graph)


def matrix_algorithm_cfg_and_graph_from_file(
    graph_filename: Path, cfg_filename: str, start_symbol="S"
) -> set[tuple[object, Variable, object]]:
    """
    Context free path querying by Matrix algorithm with context free grammar and graph
    @param graph_filename: filename of graph for querying
    @param cfg_filename: context free grammar filename
    @param start_symbol: start symbol of grammar
    @return: set of (Node, Variable, Node)
    """
    return matrix_algorithm_cfg_from_file(
        GraphUtils.open_graph(graph_filename), cfg_filename, start_symbol
    )
