from nltk.tokenize import word_tokenize
from collections import defaultdict
from collections import deque
import math
from kneser_ney import KneserNey

class Ngrams:
    """Class to build an ngram model."""

    def __init__(self, n):
        """Inits class Ngrams with a bunch of class fields.
        
        The fields initialized here are needed for the KneserNey class (the names here are not always the best):

        self.ngram_freqs = A defaultdict containing the frequencies of all ngrams.
        self.probs = A dict containing the Kneser-Ney smoothed probabilities of all ngrams.
        self.KN = An object of the Kneser-Ney class.
        self.ngram_lists = The frequencies of all ngrams organized after length.
        self.no_final_word_counts = A nested defaultdict containing the counts of the ngrams without their final words.
        self.continuation_counts = A nested defaultdict containing counts of often an ngram is a continuation of another ngram.
        self.continuation_counts_lower_ngram_strings = A nested defaultdict containing counts of often an ngram without the last word is a continuation of another ngram.
        self.succeeding_counts = A nested defaultdict containing counts of how many final word types succeed an ngram without the final word.
        self.prefixes = A nested defaultdict containing ngram prefixes as key, and a set of the full ngrams they are prefix of.
        """
        self.n = n
        self.ngram_freqs = defaultdict(int)
        self.probs = dict()
        self.KN = None
        self.ngram_lists = defaultdict(lambda: defaultdict(int))
        self.no_final_word_counts = defaultdict(lambda: defaultdict(int))
        self.continuation_counts = defaultdict(lambda: defaultdict(set))
        self.continuation_counts_lower_ngram_strings = defaultdict(lambda: defaultdict(set))
        self.succeeding_counts = defaultdict(lambda: defaultdict(set))
        self.no_first_word = defaultdict(lambda: defaultdict(set))

    def build_model(self):
        """Driver function to create an ngram model."""

        print('Börjar skapa modellen...')
        print('Börjar med KN...')
        self.KN = KneserNey(self.ngram_freqs, self.ngram_lists, self.no_final_word_counts, 
                            self.continuation_counts, self.continuation_counts_lower_ngram_strings,
                            self.succeeding_counts, self.no_first_word)
        print('Tagit fram KN-objektet, börjar med sannolikheterna...')
        self._get_probabilities()
        print('Strukturerar...')
        return self._structure()

    def create_ngrams(self, sentence):
        """Creates ngrams with length = 1,...,n from a given sentence.
        
        Uses the helper function _add_ngrams() to create the ngrams.

        Also counts each ngram's frequency
        
        Note that the function will create ngrams of all the lower orders of n aswell.
        If n = 3, the function will create unigrams, bigrams and trigrams.
        
        All ngrams and frequencies are saved to self.ngram_freqs.
        
        Args:
            sentence: An untokenized sentence.
            n: The highest order of the ngrams to be created."""

        n = self.n
        self.ngram_freqs[tuple(['[UNK]'])] = 0  # Handle unknown strings
        for i in range(1, n+1):
            self._add_ngrams(sentence, n=i)

    def _add_ngrams(self, sentence, n):
        """Creates ngrams from a sentence and adds them to self.ngram_freqs.
        
        Continuously adds words to a deque. When the length of the deque = n,
        saves contents of deque to self.ngram_freqs and increments its frequency with 1.
        Then pops the leftmost word of the deque and starts over.
        
        Also adds padding to beginning and end of sentence.
        
        Also adds counts to various other frequency dicts (see __init__)."""

        sentence = word_tokenize(sentence)
        start = '<s>'
        end = '</s>'
        
        sentence[0:0] = [start] * n
        sentence.extend([end] * n)
        ngram = deque()

        for i in range(len(sentence)):
            ngram.append(sentence[i].lower())
            if len(ngram) == n:
                self.ngram_freqs[tuple(ngram)] += 1
                self.ngram_lists[n][tuple(ngram)] += 1
                self.no_final_word_counts[tuple(ngram)[:-1]][tuple(ngram)] += 1
                if n > 1:
                    self._count_successions(tuple(ngram), n)
                if n > 2: 
                    self._count_continuations(tuple(ngram), n)
                ngram.popleft()

    def _get_probabilities(self):
        """Uses the KneserNey class to get the probabilities of an ngram."""

        n = 0
        max = len(self.ngram_freqs)
        part = 100000
        for ngram in self.ngram_freqs:
            if ngram != ('[UNK]',):
                self.KN._highest_order = len(ngram)
                self.probs[ngram] = math.log(self.KN.kneser_ney(ngram, train=True))
            n += 1
            if n % part == 0:
                print(f'{round((n / max)*100, 2)}% processat, ({n} utav {max} antal ngrams)')

    def _count_continuations(self, ngram, n):
        """Adds counts to the continuation dicts. (see __init__ for)"""
        self.continuation_counts[n-1][ngram[1:]].add(ngram)
        self.continuation_counts_lower_ngram_strings[n-1][ngram[-(n-2):]].add(ngram)
                
    def _count_successions(self, ngram, n):
        """Counts how many word types that can succeed the string: the ngram without the final word"""
        self.succeeding_counts[n][ngram[:-1]].add(ngram[-1])

    def _no_first_word(self, ngram, n):
        self.no_first_word[n][ngram[1:]].add(ngram)

    def _structure(self):
        """Puts all the ngrams with their probabilities into a dict structured after the length of the ngram."""

        structured_probs = defaultdict(lambda: defaultdict(list))

        n = 0
        max = len(self.ngram_freqs)
        part = 50000
        for ngram, prob in self.probs.items():
            if len(ngram) == 1:
                structured_probs[len(ngram)][ngram[0]] = (ngram[0], prob)
            structured_probs[len(ngram)][ngram[:-1]].append((ngram, prob))

            n += 1
            if n % part == 0:
                print(f'{round((n / max)*100, 2)}% processat, ({n} utav {max} antal ngrams)')

        return dict(structured_probs), self.probs
