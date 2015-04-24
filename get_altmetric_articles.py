##########################################################################
#
# Name: Top Altmetric Article RSS Generator
# Author: Matt Herron
# Date: 4/16/2015
# Description: Gets the top n Altmetric articles and publishes an rss 
# feed of those articles
#
##########################################################################
import urllib
import urllib2
import json
import sys
import os
import xml.etree.ElementTree as ET
from email.Utils import formatdate
from datetime import datetime
import shutil

##########################################################################
#
#						   F U N C T I O N S
#
##########################################################################
def get_file_size(filename):
	fileObj = open(filename, 'rb')
	fileObj.seek(0,2)
	fileSize = fileObj.tell()
	fileObj.close()
	return fileSize

#function to generate rss template
def generate_rss_template(filename):
	#generate empty RSS xml file with single root
	rssTemplate = open(filename, 'w+b')

	#write xml file header
	rssTemplate.write('<?xml version="1.0" encoding="UTF-8"?>\r\n')

	#write the RSS xml root element
	rssTemplate.write('<rss version="2.0">\r\n')
	rssTemplate.write('\t<channel>\r\n')
	rssTemplate.write('\t\t<title>Top 10 Altmetric Articles from The JAMA Network</title>\r\n')
	rssTemplate.write('\t\t<link>http://jamanetwork.com</link>\r\n')
	rssTemplate.write('\t\t<description>A regularly updated feed of JAMA Network articles getting the highest attention score for the past week</description>\r\n')
	rssTemplate.write('\t\t<language>en</language>\r\n')
	rssTemplate.write('\t\t<generator>Python 2.7.6</generator>\r\n')
	rssTemplate.write('\t\t<copyright>Copyright ' + str(datetime.now().year) + ' American Medical Association</copyright>\r\n')
	rssTemplate.write('\t\t<pubDate>' + formatdate() + '</pubDate>\r\n')
	rssTemplate.write('\t\t<lastBuildDate>' + formatdate() + '</lastBuildDate>\r\n')
	rssTemplate.write('\t\t<image>http://jamanetwork.com/ImageLibrary/jamanetwork/jn_monogram_red.jpg</image>\r\n')
	rssTemplate.write('\t</channel>\r\n')
	rssTemplate.write('</rss>')

	#return RSS XML file object
	return rssTemplate

def get_rss_root(fileObj):
	#define parsed XML object from file
	tree = ET.parse(fileObj.name)

	#define xml document root
	root = tree.getroot()

	#return root and tree objects
	return root, tree

def write_rss_file(element, filename):
	#write modified XML object to file
	rssXMLString = ET.tostring(element, encoding="UTF-8")
	fileObj = open(filename, 'w+b')
	fileObj.write(rssXMLString)
	fileObj.close()


def get_altmetric_top(numArticles, journals, duration):
	#declare api root
	apiRoot = 'http://www.altmetric.com/api/v1/citations/'

	#iterate on journals array to create comma seperated values string of journal ids
	journalString = ""
	for journal in journals:
		journalString += (journal + ",")
	journalString = journalString[0:-1]

	#build query parameter dictionary
	queryParams = {'journals': journalString,
					'key': 'cffe6a76e3868d735272eb8ae3de71b7',
					'num_results': numArticles,
					'order_by': 'score'}

	#create query string from parameter dictionary using urllib2
	queryString = urllib.urlencode(queryParams)

	#build the final query URL
	query = apiRoot + duration + "?" + queryString

	#try AltMetric API
	try:
		print query
		dataset = json.load(urllib2.urlopen(query, timeout=400))
	except urllib2.URLError, e:
		raise MyException("There was an error: %r" % e)

	#return dataset
	return dataset

def get_altmetric_badge_size(url):
	#fetch the image from URL
	imageFile = urllib2.urlopen(url)
	#get the request data from the URL call
	meta = imageFile.info()
	#parse the length of the file from response header
	return meta.getheaders("Content-Length")[0]



def get_journal_ids(journalID):
	#takes a silverchair journal ID and outputs a list of Altmetric journal IDs
	outList = []
	jids = {'174': '54d8989b2a83eea31c8b4567',
			'69': '53bd372b2a83eef6128b4567',
			'74': '53bd372b2a83eef6128b456b',
			'70': '53bd372b2a83eef6128b456d',
			'72': '53bd372b2a83eef6128b4569',
			'76': '53bd372b2a83eef6128b456e',
			'75': '53bd372b2a83eef6128b456c',
			'73': '53bd372b2a83eef6128b456a',
			'68': '53bd27942a83ee30748b4567',
			'71': '53bd372b2a83eef6128b4568',
			'67': '4f6fa4ee3cf058f610002c38'}
	# '0' is a wildcard that outputs all journals to the output list otherwise its a list of one ID		
	if (journalID == '0'):
		for key, value in jids.iteritems():
			outList.append(value)
	else:
		outList.append(jids[journalID])

	return outList

def get_journal_id_from_doi(doi):
	#hack the doi string to get the journal's id from it
	doiJournal = doi[8:doi.find('.', 3)]

	#translate doi into SCM6 journal code
	journals = {'jama': '67',
				'jamafacial': '69',
				'jamadermatol': '68',
				'jamapsychiatry': '70',
				'jamainternmed': '71',
				'jamaneurol': '72',
				'jamaoncol': '174',
				'jamaophthalmol': '73',
				'jamaoto': '74',
				'jamapediatrics': '75',
				'jamasurg': '76'}

	return journals[doiJournal]

def get_scm6_article_by_doi(doi, clientid=3):
	env = "http://api"

	#get the SCM6 journal id from doi param
	journalid = get_journal_id_from_doi(doi)

	#build query in RESTful syntax
	root = env + ".silverchair.com/v4/apiservice/client/" + str(clientid) + "/articlecontent/journal/" + journalid + "/?"
	query_params = {
		"sharedKey" : "36A5A486-C63D-4D91-9B37-963BE17EA203",
		"doi": doi,
		"articleCount" : "1"
	}
 
	query_string = urllib.urlencode(query_params)
	query = root + query_string
	print query

	#try SCM6 API
	try:
		datapull = json.load(urllib2.urlopen(query, timeout=800))
	except:
		# decoding failed
		print "ERROR: API Call Failed: ", query, sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]

	return datapull

#SAMPLE API CALLS
#http://www.altmetric.com/api/v1/citations/1w?num_results=100&key=cffe6a76e3868d735272eb8ae3de71b7&journals=54d8989b2a83eea31c8b4567%2C53bd372b2a83eef6128b4567%2C53bd372b2a83eef6128b456b%2C53bd372b2a83eef6128b456d%2C53bd372b2a83eef6128b4569%2C53bd372b2a83eef6128b456e%2C53bd372b2a83eef6128b456c%2C53bd372b2a83eef6128b456a%2C53bd27942a83ee30748b4567%2C53bd372b2a83eef6128b4568%2C4f6fa4ee3cf058f610002c38&order_by=score
#http://api.silverchair.com/v4/apiservice/client/3/articlecontent/journal/67/?doi=10.1001%2Fjama.2015.3058&sharedKey=36A5A486-C63D-4D91-9B37-963BE17EA203&articleCount=1


def get_SCM6_metadata(data):
	#initialize SCM6 dataset containing article meta data for top 10
	SCM6DataSet = {}

	#get SCM6 meta data for each article in top 10
	for article in data['results']:
		#get SCM6 article data for current article
		scData = get_scm6_article_by_doi(article['doi'])
		scPubDate = scData['ArticleDate']
		scTitle = scData['Title']
		scDOI = scData['Doi']
		scVolume = scData['Volume']
		scIssue = scData['IssueNo']
		scStartPage = scData['StartPage'],
		scEndPage = scData['EndPage']
		scURL = scData['ArticleUrl']
		#check to see if there are any authors in the SC article response
		if (scData['Authors'] is not None):
			scNumAuthors = len(scData['Authors'])
			scFirstAuthor = scData['Authors'][0]['FullName']
		else:
			scFirstAuthor = ""
			scNumAuthors = 0
		

		SCM6DataSet[article['doi']] = {
				'pubdate': scPubDate,
				'title': scTitle,
				'doi': scDOI,
				'volume': scVolume,
				'issue': scIssue,
				'startpage': scStartPage,
				'endpage': scEndPage,
				'url': scURL,
				'firstauthor': scFirstAuthor,
				'numauthors': scNumAuthors
				}

	return SCM6DataSet

def throw_exception(msg, execute_info, logFileObj):
	# print error to stdout
	print "[" + formatdate() + "]\t" + "[" + msg + "]\t", str(execute_info)
	#write error to log file
	logFileObj.write("[" + formatdate() + "]\t" + "[" + msg + "]\t" + str(execute_info) + "\r\n")

def write_success_log(msg, logFileObj):
	print "[" + formatdate() + "]\t" + "[" + msg + "]"
	logFileObj.write("[" + formatdate() + "]\t" + "[" + msg + "]" + "\r\n")

##########################################################################
#
#						M A I N  P R O G R A M
#
##########################################################################
logfilename = 'app.log'

#get the path to the local private directory of script
#make sure there is a '/' at the end of the directory sctring passed in
localDirectory = sys.argv[1]
if (not localDirectory.endswith('/')):
	localDirectory += "/"

#get the path of the directory for live rss file
#make sure there is a '/' at the end of the directory sctring passed in
webDirectory = sys.argv[2]
if (not webDirectory.endswith('/')):
	webDirectory += "/"

#get the journal ID (or wildcard) from the sys args list to determine what journal will be generated
#assume a string is inputted
selectedJournal = sys.argv[3]

#get the file name of the resulting rss feed to generate
rssFileName = sys.argv[4]

#check to see if the log file exists and if it is greater than 100MB
if (os.path.isfile(localDirectory + logfilename) and get_file_size(localDirectory + logfilename) > 100000000):
	os.remove(localDirectory + logfilename)

#open or create log file
logFile = open(localDirectory + logfilename, 'ab')

print "log file size= " + str(get_file_size(localDirectory + logfilename))

########need to log script start (date time and parameters)
write_success_log('Started process "python ' + os.path.basename(__file__) + ' ' + sys.argv[1] + ' ' + sys.argv[2] + ' ' + sys.argv[3] + ' ' + sys.argv[4] + '"', logFile)

#create file extension with date for local copy of RSS feed
#first create a 8 digit date string
today = datetime.now().strftime('%Y%m%d')
rssFileNameRoot =  rssFileName
rssFileName += ("." + today)

try:
	#Generate the RSS file template object
	rssTemplate = generate_rss_template(rssFileName)
	rssTemplate.close()
	write_success_log('Successfully generated RSS template file', logFile)
except Exception, err:
	#otherwise write errors to log file
	execution_info = err
	throw_exception('RSS template failed to generate', execution_info, logFile)

try: 
	#Create parsed XML root and tree object
	rssRoot, rssTree = get_rss_root(rssTemplate)
	write_success_log('Successfully parsed RSS template file', logFile)
except Exception, err:
	#otherwise write errors to log file
	execution_info = err
	throw_exception('RSS template failed to parse', execution_info, logFile)	

try:
	#get top 10 AltMetric articles in last week from API
	topArticles = get_altmetric_top(10, get_journal_ids(selectedJournal), '1w')
	#get the SCM6 metadata for each of the top altmetric results
	topArticlesSC = get_SCM6_metadata(topArticles)
	write_success_log('Successfully retrieved results from API services', logFile)
except Exception, err:
	#otherwise write errors to log file
	execution_info = err
	throw_exception('Failed to retrieve results from API services', execution_info, logFile)

#try to generate XMLTree for RSS
try:
	#go through each article item that comes back from AltMetric
	for article in topArticles['results']:
		#create a new item 
		item = ET.SubElement(rssRoot.find('channel'), 'item')
		#create a title for new item
		itemTitle = ET.SubElement(item, 'title')
		#write title to the title element
		itemTitle.text = article['title']
		#create guid element
		itemGUID = ET.SubElement(item, 'guid')
		#set permalink attribute to false
		itemGUID.set('isPermaLink', 'false')
		#assign DOI as guid value
		itemGUID.text = article['doi']
		#get pubdate from sc feed
		itemPubDate = ET.SubElement(item, 'pubDate')
		#set scm6 article date as formatted date string
		dateObject = datetime.strptime(topArticlesSC[article['doi']]['pubdate'], '%m/%d/%Y')
		itemPubDate.text = dateObject.strftime("%a, %d %b %Y %H:%M:%S +0000")
		#create description element
		itemDescription = ET.SubElement(item, 'description')
		#set AltMetric absctract as description
		try:
			itemDescription.text = article['abstract'][0:300] + '...'
		except KeyError:
			itemDescription = ""
		#put SCM6 article URL in the link field
		itemLink = ET.SubElement(item, 'link')
		itemLink.text = topArticlesSC[article['doi']]['url']

		#create the source RSS element
		itemSource = ET.SubElement(item, 'source')
		itemSource.text = article['images']['medium']
		itemSource.set('url', article['images']['medium'])

		#create author field and fill it with first author
		itemAuthor = ET.SubElement(item, 'author')
		itemAuthor.text = topArticlesSC[article['doi']]['firstauthor']

		if (int(topArticlesSC[article['doi']]['numauthors']) > 1): 
			itemAuthor.text += ', et al'

	#write success log to log file if iteration completes with no error
	write_success_log('XML tree successfully processed', logFile)
except Exception, err:
	#otherwise write errors to log file
	execution_info = err
	throw_exception('XML tree failed to process', execution_info, logFile)

## Do we want to not write if exception above???
#try to write new XML to RSS file
try:
	#commit changes to xml file
	write_rss_file(rssRoot, rssFileName)
	#write success message to log file after successfully writing XML to output
	write_success_log('XML successfully written to file', logFile)
except Exception, err:
	#otherwise write error to log file
	execution_info = err
	throw_exception('XML failed to write out to file', execution_info, logFile)

#try to copy the generated file to the webDirectory with .rss extension
try:
	shutil.copy2(localDirectory + rssFileName, webDirectory + rssFileNameRoot + '.rss')
	write_success_log('RSS successfully copied to web directory', logFile)
except Exception, err:
	#otherwise write error to log file
	execution_info = err
	throw_exception('RSS failed to copy to web directory', execution_info, logFile)

###### write script close (date time)
write_success_log('Ended process', logFile)

#close the log file
logFile.close()






