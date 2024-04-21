# Kneser-Ney Ngram Language Model

An ngram language model!

Can generate a sequence of tokens given a first starter token, by using ngram-probabilities based on its dataset. For instance, if 5-grams are used, the model will generate the most probable token given the 4 previous tokens:

$P(w_n|w_{n-1}w_{n-2}w_{n-3}w_{n-4})$

The generate function will continue to generate tokens until the end-of-sequence token is predicted after which the entire predicted sequence will be printed.

To handle out-of-vocabulary tokens and unseen ngram combinations, Kneser-Ney smoothing is utilized.

Dependencies:
NLTK

Kneser-Ney smoothing:
https://medium.com/@dennyc/a-simple-numerical-example-for-kneser-ney-smoothing-nlp-4600addf38b8
https://web.stanford.edu/~jurafsky/slp3/3.pdf
