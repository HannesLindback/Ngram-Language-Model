from build_model import BuildModel
import pickle
from collections import deque

class Main:

    def __init__(self) -> None:
        
        # N:
        self.n = 5
        self.model = None

    def create_model(self):
        build_model = BuildModel(self.n)
        file = 'C:/Users/hantz/Documents/Programmering/Verktyg/data/Bloggmix/bloggmix.dat'
        pickle_file = 'bloggmix_n=5_ngrams.pickle'
        csv_file = 'bloggmix_n=5_ngrams.csv'
        pickle_ngrams = 'bloggmix_ngrams_model.pickle'
        build_model.build_cache(file=file, pickle_file=pickle_file, csv_file=csv_file, 
                                pickle_ngrams=False, max=466521)

    def read_model(self):
        print('Loading model...')
        pickle_file = 'C:/Users/hantz/Documents/Programmering/Verktyg/data/Ngrams/bloggmix_n=5_ngrams.pickle'
        with open(pickle_file, 'rb') as p:
            self.model = pickle.load(p)
        print('Finished.')


    def _get_best(self, prefix, n):
        if isinstance(prefix, str):
            prefix = (prefix,)

        best = (None, float('-inf'))
        for ngram, prob in self.model[n][tuple(prefix)]:
            if prob > best[1]:
                best = (ngram, prob)
        return best
    
    def generate_sentence(self, first_word, n=5):
        generated = [first_word]
        prefix = ['<s>']*(n-2) + [first_word.lower()]

        while True:
            best = self._get_best(prefix, n)
            
            if best[0] is None:
                return 'Word not first word.\n'
                

            generated.append(best[0][-1])
            
            if best[0][-1] == ('</s>'):
                break

            prefix.append(best[0][-1])
            prefix = prefix[-4:]
            
        if generated[-1] == '</s>':
            generated = generated[:-1]
        
        sentence = ''
        for n, word in enumerate(generated):
            if word in '.,;:' or n == 0:
                sentence += word
            else:
                sentence += ' ' + word
        return sentence
    

if __name__ == '__main__':
    main = Main()
    main.read_model()

    while True:
        word = input('Enter first word\n')
        print(main.generate_sentence(word))        
