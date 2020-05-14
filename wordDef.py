import nltk
import random
from nltk.corpus import wordnet

# Input: a string
# Output: a string which is one definition of the word
def getDefinition(word):
	synset = wordnet.synsets(word)
	
	if (len(synset)==0):
		return ""
	return synset[0].definition()


# Input: a string
# Output: a set with format { "string" : definition }
# Each word / definition only appears once
def getRelated(word,typ = "hyponyms"):
	synset = wordnet.synsets(word)
	res = {}
	defSet = {}
	
	for s in synset:
		lemmaS = s.lemmas()
		hyponymSets = s.hyponyms()
		if (typ=="synonyms"):
			hyponymSets = [s]
		if (typ=="hypernyms"):
			hyponymSets = s.hypernyms()
		if (typ=="antonyms"):
			hyponymSets = s.antonyms()
		for h in hyponymSets:
			lemma = h.lemmas()
			if (len(lemma)==0):
				continue
			w = lemma[0].name()
			
			if (w==word):
				continue
			if (w in res):
				continue
			
			if (w.isalpha()):
				definition = h.definition()
				if (definition in defSet):
					continue
				res[w] = definition
				defSet[definition] = ""

	return res

def merge(fi,se):
	defSet = {}
	for w in fi:
		defSet[fi[w]] = ""
	for w in se:
		if (w in fi):
			continue
		if (se[w] in defSet):
			continue
		fi[w] = se[w]
	return fi


def chooseQuestions(word,n=4):
	s = getRelated(word,"hyponyms")
	typ = ["synonyms","hypernyms","antonyms"]
	for t in typ:
		if (len(s)>=n):
			break
		s = merge(s,getRelated(word,t))

	best = {}
	not_best = {}
	for w in s:
		if (word in w):
			not_best[w] = s[w]
			continue
		if (word in s[w]):
			not_best[w] = s[w]
			continue
		best[w] = s[w]
	
	res = {}
	ke = random.sample(best.keys(),min(n,len(best))) + random.sample(not_best.keys(),n-min(n,len(best)))	
	for k in ke:
		res[k] = s[k]
	
	return res
	
	

