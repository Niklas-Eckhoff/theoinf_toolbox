import itertools
from collections import defaultdict
from pprint import pprint


def main():
    print('Example 1:')
    G = GrammarBuilder().rules('S', ['AŚ', 'AY', 'BX', 'CS', 'c']).rule('Ś', 'BC').rules('X', ['AS', 'BQ', 'a']).rule(
        'Q', 'XX').rules('Y', ['BS', 'AÝ', 'b']).rule('Ý', 'YY').rule('A', 'a').rule('B', 'b').rule('C', 'c').build()
    pprint(G.cyk('aababb'))

    print('\nExample 2:')
    H = GrammarBuilder().rules('S', ['AT', 'AB']).rule('T', 'SB').rule(
        'A', 'a').rules('B', ['AC', 'a', 'c']).rule('C', 'c').build()
    pprint(H.cyk('aaaca'))

    print('\nExample 3:')
    T = H.universal_word_problem_algo(len('aaaca'))
    # for i, t in enumerate(T):
    #     print(f'T^{len("aaaca")}_{i}', '\n', t, '\n')
    print('aaaca' in T[-1])


class Grammar:
    def __init__(self, vars: [str], sigma: [str], productions: defaultdict, starting_symbol: str):
        self.vars = vars
        self.sigma = sigma
        self.productions = productions
        self.starting_symbol = starting_symbol

    def produces_to(self, rhs: str) -> [str]:
        lhs = []
        for key, values in self.productions.items():
            for value in values:
                if value == rhs:
                    lhs.append(key)
        return lhs

    def cyk(self, word: str) -> [[[str]]]:
        n = len(word)
        table = [[[] for _ in range(n-i)] for i in range(n)]

        for j, c in enumerate(word):
            assert c.islower()
            table[0][j] = self.produces_to(c)

        for i in range(1, n):
            for j in range(n - i):
                for k in range(i):
                    subwords = itertools.product(
                        table[k][j], table[i-k-1][j+k+1])
                    for subword in subwords:
                        subword = ''.join(subword)
                        new_words = self.produces_to(subword)
                        for new_word in new_words:
                            if new_word not in table[i][j]:
                                table[i][j].append(new_word)
        return table

    @staticmethod
    def __replace_permut(s: str, old: str, new: str) -> [str]:
        '''Separately replaces every occurrence of `old` in `s` and collects each replacement in a list.'''
        result = []
        pos = 0
        while True:
            pos = s.find(old, pos)
            if pos == -1:
                break
            else:
                s_new = s[:pos] + new + s[pos+len(old):]
                pos = pos + len(old)
                result.append(s_new)
        return result

    def universal_word_problem_algo(self, max_length: int) -> [[str]]:
        last_words = [self.starting_symbol]
        result = [last_words]
        while True:
            cur_words = last_words.copy()
            for lhs, rhss in self.productions.items():
                for rhs in rhss:
                    for word in last_words:
                        if len(word) + len(rhs) - len(lhs) > max_length:
                            continue
                        new_words = self.__replace_permut(word, lhs, rhs)
                        for new_word in new_words:
                            if new_word not in cur_words:
                                cur_words.append(new_word)
            if last_words != cur_words:
                result.append(cur_words)
                last_words = cur_words
            else:
                break
        return result


class GrammarBuilder:
    def __init__(self):
        self.vars = []
        self.sigma = []
        self.productions = defaultdict(list)
        self.starting_symbol = ''

    def rule(self, lhs: str, rhs: str):
        self.productions[lhs].append(rhs)
        return self

    def rules(self, lhs: str, rhs: [str]):
        self.productions[lhs].extend(rhs)
        return self

    def var(self, var):
        assert var.isupper()
        self.vars.append(var)
        return self

    def terminal(self, terminal):
        assert terminal.islower()
        self.sigma.append(terminal)
        return self

    def start(self, starting_symbol: str):
        assert starting_symbol.isupper()
        self.starting_symbol = starting_symbol
        return self

    def __infer_rest(self):
        lhs = list(self.productions.keys())
        rhs = list(self.productions.values())

        syms = lhs + rhs
        syms = list(itertools.chain.from_iterable(syms))

        inferred_vars = filter(lambda x: x.isupper(), syms)
        inferred_terminals = filter(lambda x: x.islower(), syms)

        self.vars.extend(inferred_vars)
        self.sigma.extend(inferred_terminals)

        if self.starting_symbol == '' and 'S' in self.vars:
            self.starting_symbol = 'S'
        return self

    def build(self):
        self.__infer_rest()
        assert len(self.vars) != 0
        assert len(self.sigma) != 0
        assert self.starting_symbol != ''
        assert self.starting_symbol in self.vars
        return Grammar(self.vars, self.sigma, self.productions, self.starting_symbol)


if __name__ == '__main__':
    main()
