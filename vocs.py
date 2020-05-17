from bs4 import BeautifulSoup
import requests
import json

def getLink(word):
	link = "https://www.vocabulary.com/dictionary/"+word
	return link

# Input: a string
# Output: a webpage in string
def getPage(word):
	link = getLink(word)
	page = requests.get(link)
	return page.text
	
		
# Input: 
#	content - webpage in string
# Output:
#	definition in string if it exists
#	otherwise, empty string
def getDefinition(content,defType):
	soup = BeautifulSoup(content)
	shortDefDiv = soup.findAll("p", {"class": defType})
	if (len(shortDefDiv)==0):
		return ""
	assert len(shortDefDiv)==1
	shortDefDiv = shortDefDiv[0]
	return shortDefDiv.get_text()

	
def getShortDefinitionWithWord(content):
	link = "https://vocabulary.now.sh/word/"+content
	page = requests.get(link)
	try:
		json_object = json.loads(page.text)
	except:
		return ""

	if json_object["success"]:
		return json_object["data"]
	return ""


def getShortDefinition(content):
	return getDefinition(content,"short")


def getLongDefinition(content):
	return getDefinition(content,"long")


def getInstance(content,insType):
	soup = BeautifulSoup(content)
	instanceDiv = soup.findAll("dl", {"class": "instances"})
	if (insType=="synonym"):
		matchType = "Synonyms:"
	if (insType=="antonym"):
		matchType = "Antonyms:"
	if (insType=="typeof"):
		matchType = "Type of:"
	currentType = "Synonyms:"
	res = {}
	for instance in instanceDiv:
		dtDiv = instance.findAll("dt")
		assert(len(dtDiv)==1)
		dtDiv = dtDiv[0]
		if (dtDiv.get_text()!=""):
			currentType = dtDiv.get_text()
		if (currentType==matchType):
			aDiv = instance.findAll("a",{"class": "word"})
			for wordDiv in aDiv:
				word = wordDiv.get_text()
				res[word] = ""
	
	ret = []
	for key in res:
		ret.append(key)
	
	return ret
	
def getSynonym(content):
	return getInstance(content,"synonym")

def getTypeOf(content):
	return getInstance(content,"typeof")

def getAntonym(content):
	return getInstance(content,"antonym")

def getJSON(word):

	json_dict = {}

	page = getPage(word)
	shortDef = getShortDefinition(page)
	longDef = getLongDefinition(page)
	synonym = getSynonym(page)
	typeOf = getTypeOf(page)
	antonym = getAntonym(page)
	
	json_dict["short"] = shortDef
	json_dict["long"] = longDef
	json_dict["synonym"] = synonym
	json_dict["antonym"] = antonym
	json_dict["typeof"] = typeOf
	
	return json.dumps(json_dict, indent = 4)
