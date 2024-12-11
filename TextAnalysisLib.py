"""
Author: Mika Nguyen

File:

Description: A reusable library for text analysis and comparison
In theory, the framework should support any collection of texts
of interest (though this might require the implementation of some
custom parsers.)

"""
import matplotlib.pyplot as plt
import pandas as pd
import sankey as sk
import re
import numpy as np
import requests
from bs4 import BeautifulSoup
import string
from collections import defaultdict, Counter
from textblob import TextBlob

class TextAnalysisLibrary:

    def __init__(self):
        """ Constructor

        datakey --> (filelabel --> datavalue)
        """
        self.data = defaultdict(dict)
        self.stop_words = set()

    def default_parser(self, filename):
        """ Parse a standard text file and produce
        extract data results in the form of a dictionary. """

        with open(filename, 'r') as file:
            text = file.read()
        text = re.sub(r"[‘’“”'\"`]", "", text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower().split()

        words = []
        for word in text:
            if word not in self.stop_words:
                words.append(word)
        wc = Counter(words)
        num_words = sum(wc.values())
        word_lengths = Counter(len(word) for word in words)

        word_sentiments = {
            word: {
                'polarity': TextBlob(word).sentiment.polarity,
                'subjectivity': TextBlob(word).sentiment.subjectivity
            }
            for word in words
        }

        results = {
            'wordcount': wc,
            'numwords' : num_words,
            'sentiment': word_sentiments,
            'word_lengths': word_lengths
        }
        return results

    def custom_parser(self, file):
        """ domain specific parser """
        response = requests.get(file)

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        text = re.sub(r"[‘’“”'\"`]", "", text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower().split()

        words = [word for word in text if word not in self.stop_words]
        wc = Counter(words)
        num_words = sum(wc.values())
        word_lengths = Counter(len(word) for word in words)
        word_sentiments = {
            word: {
                'polarity': TextBlob(word).sentiment.polarity,
                'subjectivity': TextBlob(word).sentiment.subjectivity
            }
            for word in words
        }

        results = {
            'wordcount': wc,
            'numwords': num_words,
            'sentiment': word_sentiments,
            'word_lengths': word_lengths
        }
        print(results)
        return results

    def stop_words_url(self, url):
        """ implement stop words to sort"""
        file = requests.get(url).content
        self.stop_words = set(file.decode().splitlines())

    def load_stop_words(self, filename):
        """ stop words file - specific to dating apps """
        with open(filename, 'r', encoding='utf-8') as file:  # Use utf-8 encoding
            self.stop_words = set(file.read().splitlines())

    def load_text(self, filename, label=None, parser=None):
        """ Register a document with the framework.
        Extract and store data to be used later by
        the visualizations """

        if parser is None:
            results = self.default_parser(filename)
        else:
            results = parser(filename)

        if label is None:
            label = filename

        for key, val in results.items():
            self.data[key][label] = val

    def wordcount_sankey(self, word_list=None, k=3):
        """ Map each text to words using a Sankey diagram
        Thickness of the line is the number of time the word occurs in the text
        Users can specify a particular set of words, or the words can be the union
        of the k most common words across each text file """

        word_counts = self.data['wordcount']
        all_words = set()

        if word_list:
            all_words.update(word_list)
        else:
            for wc in word_counts.values():
                all_words.update([word for word, _ in wc.most_common(k)])

        sk_data = []
        for label, wc in word_counts.items():
            for word in all_words:
                if word in wc:
                    sk_data.append({'src': label, 'targ': word, 'val': wc[word]})

        df = pd.DataFrame(sk_data)
        sk.make_sankey(df, src='src', targ='targ', vals='val')

    def most_common_words(self, k=10):
        """
        Bar charts showing the most common words in each text file.
        k: Number of most common words to display.
        """
        data = self.data['wordcount']
        num_files = len(data)

        cols = 2
        rows = (num_files + 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
        axes = axes.flatten()

        for i, (label, wc) in enumerate(data.items()):
            most_common = wc.most_common(k)
            words, counts = zip(*most_common)
            axes[i].barh(words, counts, color='#7AA2C4')
            axes[i].set_title(f'{label}')
            axes[i].set_xlabel('Frequency')
            axes[i].invert_yaxis()

        for ax in axes:
            ax.set_xlim([0, 50])

        fig.suptitle('Most Common Words Used in Advertisement and Reviews', fontsize=16)
        plt.tight_layout()
        plt.show()

    def plot_sentiment(self):
        """
        Subplots of scatterplots showing sentiment scores (polartity vs subjectivity) for each file
        """
        data = self.data['sentiment']
        num_files = len(data)
        cols = 2
        rows = (num_files + 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(15, 4 * rows))
        axes = axes.flatten()

        for i, (label, sentiments) in enumerate(data.items()):
            pol = []
            sub = []
            for word, sentiment in sentiments.items():
                pol.append(sentiment['polarity'])
                sub.append(sentiment['subjectivity'])
            axes[i].scatter(pol, sub, alpha=0.4)
            axes[i].set_title(f'{label}')
            axes[i].set_xlabel('Polarity')
            axes[i].set_ylabel('Subjectivity')

        for ax in axes:
            ax.set_xlim([-1.1, 1.1])

        fig.suptitle('Sentiment Scores Across Dating Platforms for Advertisement and their Reviews', fontsize=16)
        plt.tight_layout()
        plt.show()

    def stacked_bar(self, k=10):
        """ Stacked bar chart showing word distribution across multiple files."""
        word_counts = self.data['wordcount']
        all_words = {file: Counter() for file in word_counts}

        for file, wc in word_counts.items():
            all_words[file].update(wc)

        all_words_combined = Counter()
        for wc in all_words.values():
            all_words_combined.update(wc)

        most_common = all_words_combined.most_common(k)
        words = [word for word, count in most_common]

        word_counts_per_file = np.array([[all_words[file].get(word, 0) for word in words] for file in all_words])

        fig, ax = plt.subplots(figsize=(10, 6))
        bottom = np.zeros(len(words))
        for i, file in enumerate(all_words.keys()):
            ax.barh(range(len(words)), word_counts_per_file[i], left=bottom, label=file)
            bottom += word_counts_per_file[i]

        ax.set_yticks(range(len(words)))
        ax.set_yticklabels(words)
        ax.set_ylabel("Words")
        ax.set_xlabel("Word Counts")
        ax.set_title(f"Top {k} Most Common Words Across Files")
        ax.invert_yaxis()
        ax.legend(title="Files")
        plt.tight_layout()
        plt.show()