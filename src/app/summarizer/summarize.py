from fuzzywuzzy.process import dedupe 
from gensim.summarization import summarize 
from textblob import TextBlob 
import pke 
import nltk
import uuid
import os
nltk.download('stopwords')


class Summarizer():

	def __init__(self,text):
		self.text = list(dedupe(text))
		paragraph = ''
		for sentence in self.text:
		  paragraph += sentence+'. '
		self.paragraph = paragraph


	def get_summary(self):
	    num_of_words = len(self.paragraph.split())
	 
	    if num_of_words >= 5000:
	        return (summarize(self.paragraph,0.05))
	    elif num_of_words >= 3000 and num_of_words < 5000 :
	        return (summarize(self.paragraph,0.1))
	    elif num_of_words >= 1000 and num_of_words < 3000 :
	        return (summarize(self.paragraph,0.2))
	    else:
	        return (summarize(self.paragraph,0.3))

	def get_keyphrases(self):
		extractor = pke.unsupervised.TextRank()
		filename = str(uuid.uuid1())+'.txt'
		f = open(filename, "w")
		f.write(self.paragraph)
		f.close()
		extractor.load_document(input=filename, language='en')
		os.remove(filename) 		
		extractor.candidate_selection()
		extractor.candidate_weighting()
		keyphrases = extractor.get_n_best(n=10)
		return keyphrases