"""
Module containing a Kneser Ney smoothing algorithm.

NOTE: Since the workings of the Kneser-Ney smoothing is quite complex I won't try to explain it here.
      If you want to understand how it works I recommend the description in Jurafsky chapter 3 or 
      this webpage: https://medium.com/@dennyc/a-simple-numerical-example-for-kneser-ney-smoothing-nlp-4600addf38b8
      All comments are made with the assumption that the reader understands how Kneser-Ney works.
"""

class KneserNey:

    def __init__(self, ngram_freqs, ngram_lists, no_final_word_counts, continuation_counts, 
                 continuation_counts_lower_ngram_strings, succeeding_counts, no_first_word):
        """Inits KneserNey with a bunch of class fields. Most class fields are explained in ngrams.py.

        self._highest_order = The highest order of the ngram processed.
        self._D = A dictionary containing the various d constants. Which one is used depends on the frequency of the ngram.
        self._d = The current d constant used for the ngram.
        self._ngram = The ngram currently being processed.
        """

        self._ngram_freqs = ngram_freqs
        self._highest_order = None
        self._ngram = None
        self._ngram_lists = ngram_lists
        self._D = self._get_D()
        self._d = None
        self._no_final_word_counts = no_final_word_counts
        self._continuation_counts = continuation_counts
        self._continuation_counts_lower_ngram_strings = continuation_counts_lower_ngram_strings
        self._succeeding_counts = succeeding_counts
        self._no_first_word = no_first_word

    def kneser_ney(self, ngram, train=False, get_prob=False):
        """Gets the Kneser-Ney smoothed probability of the given ngram."""

        if self._unknown_word(ngram):
            ngram = ('[UNK]',)
            return self._unknown_word_prob(ngram)

        self._ngram = ngram

        if train:
            return self._P_KN(self._ngram)

        elif get_prob:
            ngrams = self._no_first_word[len(self._ngram)][self._ngram[1:]]
            if len(ngrams) != 0:
                P_KN = max([self._P_KN(ngram) for ngram in ngrams])  # Undrar hur det skulle vara om man returnerade snittet?
                return P_KN
            else:
                return self.kneser_ney(self._ngram[1:])

    def _P_KN(self, ngram):
        """Calculates the Kneser-Ney smoothed probability given the discount, the lambda, and the continuation probability.
        
        The continuation probability is the recursive Kneser-Ney probability of lower order ngrams. 
        For unigrams the continuation probability is the uniform probability since the lower order ngram of the unigram is the empty string."""

        self._ngram = ngram

        if self._ngram_freqs[self._ngram] >= 3:
            self._d = self._D[3]
        else:
            self._d = self._D[self._ngram_freqs[self._ngram]]

        if len(self._ngram) == 1:
            discount = self._discount()
            LAMBDA = self._lambda()
            continuation_prob = 1 / len(self._ngram_lists[len(self._ngram)])
            return discount + LAMBDA * continuation_prob

        discount = self._discount()
        LAMBDA = self._lambda()
        continuation_prob = self._P_KN(ngram[1:])
        P_KN = discount + LAMBDA * continuation_prob
        return P_KN

    def _discount(self):
        """Calculates the discount term.
        
        If ngram is unigram c_KN will be 1, since there is only the empty string preceding the string."""

        if len(self._ngram) == 1:
            return max(1 - self._d, 0) / 1
        
        discount = max(self._c_KN(self._ngram) - self._d, 0) / self._c_KN(self._ngram[:-1])
        return discount

    def _lambda(self):
        """Calculates the lambda term. 
        
        Since lambda is a function of the ngram without the final word (the string), if the ngram is a unigram,
        the frequency of the string and succeding count will be the same as 1, since there is only the empty string preceding the string."""

        if len(self._ngram) == 1:
            left_term = self._d / 1
            right_term = 1
            return left_term * right_term
        
        string = self._ngram[:-1]
        LAMBDA = self._d / self._ngram_freqs[string] * self._succeeding_count(string)
        return LAMBDA
    

    # Helper functions:
    def _c_KN(self, string):
        """Gets Kneser-Ney count (C_KN) of string.
        
        For the highest order n-gram, the Kneser-Ney count is the same as the frequency of the string.
        If the string is the full ngram only the frequency of the ngram is needed. 
        If the string is the prefix of the ngram, the frequencies of all instances of that string is needed. 
        I.e. the frequencies of the ngram where it appears are summed.
        For lower orders, C_KN is equal to the continuation count of the string.
        Continuation count: The number of different word types preceding the string."""

        assert type(string) == tuple
        
        if len(self._ngram) == self._highest_order:
            if string == self._ngram:
                c_KN = self._ngram_freqs[self._ngram]
            else:
                c_KN = 0                
                for ngram, freq in self._no_final_word_counts[string].items(): c_KN += freq 
        else:
            if string == self._ngram:
                c_KN = len(self._continuation_counts[len(self._ngram)][string])
            else:
                c_KN = len(self._continuation_counts_lower_ngram_strings[len(self._ngram)][string])
        return c_KN

    def _get_D(self):
        """Gets the value of d.

        According to the modified Kneser-Ney smoothing (Chen, 1999),
        d should be set to different values depending on if the ngram has a count of 0, 1, 2 or, 3 or more.
        This function gets these different values and puts them in a dict so that it can easily be accessible.

        I am assume that n_3 and n_4 should be the number of ngrams with counts 3 and 4 respectively,
        but as they are not explicitly defined in the paper I am not 100% that this correct."""

        n_1, n_2, n_3, n_4 = 0, 0, 0, 0
        for ngram, freq in self._ngram_freqs.items():
            if freq == 1:
                n_1 += 1
            elif freq == 2:
                n_2 += 1
            elif freq == 3:
                n_3 += 1
            elif freq == 4:
                n_4 += 1

        Y = n_1 / (n_1 + 2*n_2)
        D = dict()
        D[0] = 0
        D[1] = 1 - 2 * Y * (n_2 / n_1)
        D[2] = 2 - 3 * Y * (n_3 / n_2)
        D[3] = 3 - 4 * Y * (n_4 / n_3)
        return D

    def _succeeding_count(self, string):
        """Gets the number of word types succeding the string."""

        return len(self._succeeding_counts[len(self._ngram)][string])

    def _basecase(self):
        """Basecase for when to stop the recursion."""

        return len(self._ngram) == 1

    def _unknown_word(self, ngram):
        if len(ngram) == 1:
            return not self._ngram_freqs.get(ngram, False)
        else:
            return False
        
    def _unknown_word_prob(self, ngram):
        self._ngram = ngram
        return self._lambda() / len(self._ngram_freqs)