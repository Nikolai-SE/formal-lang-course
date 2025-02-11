from pyformlang.cfg import Variable
from pyformlang.finite_automaton import EpsilonNFA

from project.grammar import ECFG
from project.querying import TensorNFA


class RSM:
    """
    Recursive state machine
    """

    def __init__(
        self, nfa_dict: dict[Variable, EpsilonNFA], start: Variable = Variable("S")
    ):
        """
        Initialising recursive state machine
        @param nfa_dict: dictionary of Variables and EpsilonNFA
        @param start: starting Variable, default S
        """
        self.nfa_dict = nfa_dict
        self.start = start

    def get_tensor_nfa_dict(self) -> dict[Variable, TensorNFA]:
        """
        Constructs dictionary of Variable and TensorNFA
        @return: dictionary of Variable and TensorNFA
        """
        dictionary: dict[Variable, TensorNFA] = {}
        for symbol, nfa in self.nfa_dict.items():
            dictionary[symbol] = TensorNFA.from_nfa(nfa.to_deterministic())
        return dictionary

    def __getitem__(self, item) -> EpsilonNFA:
        return self.nfa_dict[item]

    def __iter__(self) -> EpsilonNFA:
        for v in self.nfa_dict.values():
            yield v
        return

    def minimize(self) -> "RSM":
        """
        minimizes each nfa at RSM and returns copy of RSM
        @return: minimized copy of RSM
        """
        min_nfa_dict: dict[Variable, EpsilonNFA] = {}
        for var, nfa in self.nfa_dict.items():
            min_nfa_dict[var] = nfa.minimize()
        return RSM(min_nfa_dict, self.start)


def rsm_from_ecfg(ecfg: ECFG) -> RSM:
    """
    Transform extended context free grammar to recursive state machine
    @param ecfg: extended context free grammar for converts
    @return: recursive state machine
    """
    nfa_dict: dict[Variable, EpsilonNFA] = {}
    for var, reg in ecfg.productions.items():
        nfa_dict[var] = reg.to_epsilon_nfa()
    return RSM(nfa_dict, ecfg.start)
