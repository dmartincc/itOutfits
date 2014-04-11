# -*- coding: utf-8 -*-
import nltk
from nltk.probability import FreqDist 
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import nltk.data
import string
import operator
import sys
import re


def isPunct(word):
  return len(word) == 1 and word in string.punctuation

def isNumeric(word):
  try:
    float(word) if '.' in word else int(word)
    return True
  except ValueError:
    return False

def sentimentAnalysis(text):
    keywords = []
    d = {}    
    train = open("app/AFINN-111_es.txt")
    list_words_train = [line.split(';') for line in train if line.strip() != ""]
    for i in range(len(list_words_train)):
        d[list_words_train[i][0]] = int(float(list_words_train[i][1]))
        
    
    key={}
    keywords.append(text.lower())
    for i in range(len(keywords)):
        key[keywords[i]] = str(keywords[i])
        
    sentiment = ['Neutral','Positive','Negative']
    words = []                    
    words.extend(text.split())
    sentiment_score = 0
    output=[]
    for word in d:
        p = re.compile(word)
        if bool(p.search(text)) == True:
            sentiment_score += d[word]               
    if sentiment_score == 0:
        out = sentiment[0]
    elif sentiment_score>0:
        out = sentiment[1]
    elif sentiment_score<0:
        out = sentiment[2]
    output.append(sentiment_score)
    output.append(out)
    
    return output
    
def extract_entities(text):
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'node'):
                print chunk.node, ' '.join(c[0] for c in chunk.leaves())

def extract_entities_regex(text):
    regexes = ('[A-Z][A-Za-záéíóúñ]{2,} [A-Z][A-Za-záéíóúñ]{2,} [A-Z][A-Za-záéíóúñ]{2,} [A-Z][A-Za-záéíóúñ]{2,}',
               '[A-Z][A-Za-záéíóúñ]{2,} [A-Z][A-Za-záéíóúñ]{2,} [A-Z][A-Za-záéíóúñ]{2,}',
               '[A-Z][A-Za-záéíóúñ]{2,} [A-Z][A-Za-záéíóúñ]{2,}',
               '[A-Z][A-Za-záéíóúñ]{2,} [A-Za-záéíóúñ]{2,3} [A-Z][A-Za-záéíóúñ]{2,}',
               '[A-Z][A-Za-záéíóúñ]{2,} [A-Z][A-Za-záéíóúñ]{2,}[-][A-Z][A-Za-záéíóúñ]{2,} [A-Z][A-Za-záéíóúñ]{2,}'
               '[A-Z]{3,}')
    regexes = [ re.compile(i,re.S) for i in regexes ]
    matches = [regexes[i].findall(text) for i in range(len(regexes))]
    entities=[]
    for regex in matches:
        for entity in regex:
            entities.append(entity)            
    return entities

def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document) 
    sentences = [nltk.word_tokenize(sent) for sent in sentences] 
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    sentences = nltk.batch_ne_chunk(sentences, binary=True)
    return sentences 

def chunker(document):  
        
    grammar = r"""
        Entities:      {<NNP>+}              # Chunk sequences of NNP's (Entity)        
        Keywords:      {<NN>+}               # Chunk prepositions followed by NP
        AdjetiveKey:   {<JJ>*<NN>}           # Chunk adjetive and nouns
        CLAUSE:        {<NP><VP>}            # Chunk NP, VP
        CHUNK:         {<NE><V.*><JJ.*>?<V.*>?<Keywords>?}    # Chunk VB to VB 
      """
    any_language =r""" 
        NP:   {<PRP>?<JJ.*>*<NN.*>+}
        CP:   {<JJR|JJS>}
	    VERB: {<VB.*>}
	    THAN: {<IN>}
	    COMP: {<DT>?<NP><RB>?<VERB><DT>?<CP><THAN><DT>?<NP>}
    """
    cp = nltk.RegexpParser(grammar)  

    tree=cp.parse(sentence[0])
    entities = []
    for subtree in tree.subtrees():
         if subtree.node == 'NE': 
            entity = []
            for word in subtree.leaves():
                entity.append(word[0])
            sent_str = ""
            for i in entity:
                sent_str += str(i) + " "
            sent_str = sent_str[:-1]  
            entities.append(sent_str)                     
    col.append(entities) 
    #Keywords
    keywords = []
    for subtree in tree.subtrees():
         if subtree.node == 'AdjetiveKey':
            entity = []
            for word in subtree.leaves():
                keywords.append(word[0])
            #keywords.append(entity)  
    #col.append(keywords) 
    #Count keywords         
    wordFreqD = {}
    for i in range(len(keywords)):            
           wordFreqD[keywords[i]] = wordFreqD.get(keywords[i], 0)+1
    sortedKeywords = sorted(wordFreqD,key=wordFreqD.get(1),reverse=True)[:5] 
    
            #Relations between NEs
    relations = []
    for subtree in tree.subtrees():
         if subtree.node == 'CHUNK':
            entity = []
            for word in subtree.leaves():
                relations.append(word[0])
                
    return sortedKeywords
        
        
class RakeKeywordExtractor:

  def __init__(self):
    self.stopwords = set(nltk.corpus.stopwords.words('spanish'))
    self.top_fraction = 0.05 # consider top third candidate keywords by score

  def _generate_candidate_keywords(self, sentences):
    phrase_list = []
    for sentence in sentences:
      words = map(lambda x: "|" if x in self.stopwords else x,
        nltk.word_tokenize(sentence.lower()))
      phrase = []
      for word in words:
        if word == "|" or isPunct(word):
          if len(phrase) > 0:
            phrase_list.append(phrase)
            phrase = []
        else:
          phrase.append(word)
    return phrase_list

  def _calculate_word_scores(self, phrase_list):
    word_freq = nltk.FreqDist()
    word_degree = nltk.FreqDist()
    for phrase in phrase_list:
      degree = len(filter(lambda x: not isNumeric(x), phrase)) - 1
      for word in phrase:
        word_freq.inc(word)
        word_degree.inc(word, degree) # other words
    for word in word_freq.keys():
      word_degree[word] = word_degree[word] + word_freq[word] # itself
    # word score = deg(w) / freq(w)
    word_scores = {}
    for word in word_freq.keys():
      word_scores[word] = word_degree[word] / word_freq[word]
    return word_scores

  def _calculate_phrase_scores(self, phrase_list, word_scores):
    phrase_scores = {}
    for phrase in phrase_list:
      phrase_score = 0
      for word in phrase:
        phrase_score += word_scores[word]
      phrase_scores[" ".join(phrase)] = phrase_score
    return phrase_scores
    
  def extract(self, text, incl_scores=False):
    sentences = nltk.sent_tokenize(text)
    phrase_list = self._generate_candidate_keywords(sentences)
    word_scores = self._calculate_word_scores(phrase_list)
    phrase_scores = self._calculate_phrase_scores(phrase_list, word_scores)
    sorted_phrase_scores = sorted(phrase_scores.iteritems(),
      key=operator.itemgetter(1), reverse=True)
    n_phrases = len(sorted_phrase_scores)
    if incl_scores:
      return sorted_phrase_scores[0:int(n_phrases*self.top_fraction)]
    else:
      return map(lambda x: x[0],sorted_phrase_scores[0:int(n_phrases*self.top_fraction)])
        
class SimpleSummarizer:

	def reorder_sentences( self, output_sentences, input ):
		output_sentences.sort( lambda s1, s2:
			input.find(s1) - input.find(s2) )
		return output_sentences

	def summarize(self, input, num_sentences ):
		# TODO: allow the caller to specify the tokenizer they want
		# TODO: allow the user to specify the sentence tokenizer they want

		tokenizer = RegexpTokenizer('\w+')

		# get the frequency of each word in the input
		base_words = [word.lower() 
			for word in tokenizer.tokenize(input)]
		words = [word for word in base_words if word not in stopwords.words()]
		word_frequencies = FreqDist(words)

		# now create a set of the most frequent words
		most_frequent_words = [pair[0] for pair in 
			word_frequencies.items()[:100]]

		# break the input up into sentences.  working_sentences is used 
		# for the analysis, but actual_sentences is used in the results
		# so capitalization will be correct.

		sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
		actual_sentences = sent_detector.tokenize(input)
		working_sentences = [sentence.lower() 
			for sentence in actual_sentences]

		# iterate over the most frequent words, and add the first sentence
		# that inclues each word to the result.
		output_sentences = []

		for word in most_frequent_words:
			for i in range(0, len(working_sentences)):
				if (word in working_sentences[i] 
				  and actual_sentences[i] not in output_sentences):
					output_sentences.append(actual_sentences[i])
					break
				if len(output_sentences) >= num_sentences: break
			if len(output_sentences) >= num_sentences: break

		# sort the output sentences back to their original order
		output_sentences = self.reorder_sentences(output_sentences, input)

		# concatinate the sentences into a single string
		return "  ".join(output_sentences)