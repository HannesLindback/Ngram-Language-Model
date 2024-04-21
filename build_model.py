import xml.etree.ElementTree as ET
from pathlib import Path
from ngrams import Ngrams
from BraProjekt.Ngrams.chunk_files import Process
import pickle
import time
from xml.etree.cElementTree import iterparse
import csv

class BuildModel:
    """Driver class to create a ngram model.
    
    Provides functions to: 
        - create a corpus out of an XML-file containing text data.
        - build a cached model which can be extracted out of the pickle file created."""

    def __init__(self, n):
        self.ngrams = Ngrams(n)

    def create_corpus(self, path, output_file):
        """Creates a corpus out of an XML-file containing text data from a UN-corpus.
        
        It is assumed that the corpus is located in several different 
        XML-files in several different nested folders. All these files
        are extracted with the use of the Path module and then each 
        processed in turn. The helper function extract_xml() extracts the text from
        each file and writes it to a new corpus file.
        
        Args:
            path: A path leading to a the directory of a corpus."""

        rootdir = Path(path)
        file_list = [f for f in rootdir.glob('**/*') if f.is_file()]
        n = 0

        for file in file_list:
            try:
                if n % 1000 == 0:
                    print(n)
                self.extract_xml(file, output_file)  
            except:
                pass
            n += 1

    def extract_xml(self, xmlpath, outputfile, max=3000000):
        """Extracts the text from an XML-file and writes it to a new file."""

        n = 0
        with open(outputfile, 'a', encoding='utf-8') as output:
            sentence = []
            for event, elem in iterparse(xmlpath):
                breakpoint
                if elem.tag == 'w':
                    sentence.append(elem.text)
                elif elem.tag == 'sentence':
                    sent = ' '.join(sentence) + '\n'
                    output.write(sent)
                    sentence.clear()
                if n % 100000 == 0:
                    print(f'{round((n / max)*100, 2)}% processed, ({n} out of {max} lines)')
                n += 1

    def build_cache(self, file, pickle_file=False, csv_file=False, pickle_ngrams=False, max=200000):
        """Builds a cached ngram-model out of the corpus provided.
        
        Uses the Ngram class in the ngram.py module to create the model.
        After the model is created, pickles the model for future use.
        Can also write all ngrams to a csv file.
        
        Args:
            file: A path to a corpus file.
            n: The highest order ngram that the model should create.
            max: The max amount of lines to be read from the corpus. 
                 The size of the model grows extremely fast with the size of n.
                 Be careful not to set n and max to high.
                 """
        
        start = time.time()
        hundredth = max / 100
        if max <= 50000:
            with open(file, 'r', encoding='utf-8') as fhand:
                m = 0
                for line in fhand:
                    self.ngrams.create_ngrams(line.rstrip('\n'))
                    m += 1
                    if m == max:
                        break
                    elif m % hundredth == 0:
                        print(f'{round((m / max)*100, 2)}% processat, ({m} utav {max} antal rader)')

        else:
            process = Process()
            process.process(file, self.ngrams.create_ngrams, max_lines=max)
            
        print(time.time() - start)

        if pickle_ngrams:
            with open(pickle_ngrams, 'wb') as picklehand:
                pickle.dump(self.ngrams, picklehand)
            exit()

        structured_ngrams, ngram_probs = self.ngrams.build_model()

        print('Picklar...')
        if pickle_file:
            with open(pickle_file, 'wb') as picklehand:
                pickle.dump(structured_ngrams, picklehand)
        
        print('Skriver till csv...')
        if csv_file:
            with open(csv_file, 'w', newline='', encoding='utf-8') as fhand:
                writer = csv.writer(fhand, delimiter=',')
                
                m = 0
                max = len(ngram_probs)
                for ngram_prob in ngram_probs.items():
                    writer.writerow([ngram_prob])
                    if m % 10000 == 0:
                        print(f'{round((m / max)*100, 2)}% processat, ({m} utav {max} antal rader)')
                    m += 1
