from django.db import models
import math


# Create your models here.

class Document(models.Model):
    title = models.CharField(max_length=1000, null=True, default='Title')
    text = models.CharField(max_length=10000, null=True, default='Sample text')
    snippet = models.CharField(max_length=300, null=True, default='Sample text')

    def get_words(self):
        words = {}
        for raw_word in self.text.split():
            if raw_word.endswith((',', '.', '-', '!', '?', ';')):
                word = raw_word[:-1]
            else:
                word = raw_word
            if word in words:
                words[word] += 1
            else:
                words[word] = 1
        return words

    @staticmethod
    def get_idf():
        documents = Document.objects.all()
        n = len(documents)
        words_count = {}
        for document in documents:
            for word in set(document.get_words().keys()):
                if word in words_count:
                    words_count[word] += 1
                else:
                    words_count[word] = 1

        words_idf = {}
        for word, p in words_count.items():
            words_idf[word] = math.log2(n / p)
        return words_idf

    def get_tf_idf(self):
        doc_word_dict = self.get_words()
        max_count = 0
        for count in doc_word_dict.values():
            if count > max_count:
                max_count = count
        tf_idf_dict = {}
        for word, idf in self.get_idf().items():
            if word in doc_word_dict:
                tf_idf_dict[word] = (doc_word_dict[word] / max_count) * idf
            else:
                tf_idf_dict[word] = 0
        return tf_idf_dict

    def get_length(self):
        tf_idf_dict = self.get_tf_idf()
        sum_of_squares = 0
        for value in tf_idf_dict.values():
            sum_of_squares += value ** 2
        return sum_of_squares ** 0.5


class Search(models.Model):
    query = models.CharField(max_length=1000, null=True, default="text")

    def get_words(self):
        words = {}
        for raw_word in self.query.split():
            if raw_word.endswith((',', '.', '-', '!', '?', ';')):
                word = raw_word[:-1]
            else:
                word = raw_word
            if word in words:
                words[word] += 1
            else:
                words[word] = 1
        return words

    def get_tf_idf(self):
        doc_word_dict = self.get_words()
        max_count = 0
        for count in doc_word_dict.values():
            if count > max_count:
                max_count = count
        tf_idf_dict = {}
        for word, idf in Document.get_idf().items():
            if word in doc_word_dict:
                tf_idf_dict[word] = (doc_word_dict[word] / max_count) * idf
            else:
                tf_idf_dict[word] = 0
        return tf_idf_dict

    def get_length(self):
        tf_idf_dict = self.get_tf_idf()
        sum_of_squares = 0
        for value in tf_idf_dict.values():
            sum_of_squares += value ** 2
        return sum_of_squares ** 0.5

    def get_result(self):
        documents = Document.objects.all()
        docs_sim = {}
        search_tf_idf = self.get_tf_idf()
        for doc in documents:
            doc_tf_idf = doc.get_tf_idf()
            numerator = 0
            for word in search_tf_idf:
                numerator += search_tf_idf[word] * doc_tf_idf[word]
            try:
                result = numerator / (self.get_length() * doc.get_length())
                if result != 0:
                    docs_sim[doc] = result
            except ZeroDivisionError:
                return list()
        return sorted(docs_sim, key=docs_sim.get, reverse=True)
