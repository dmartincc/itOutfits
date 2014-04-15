# -*- coding: utf-8 -*
import json, feedparser, datetime
from pattern.web import URL, DOM, plaintext, strip_tags, decode_entities


blogs=['http://sincerelyjules.com/feed',
       'http://www.manrepeller.com/feed',
       'http://www.purseblog.com/feed',
       'http://www.thesartorialist.com/feed',
       'http://feeds.feedburner.com/blogspot/XkbrU',
       'http://www.theblondesalad.com/feed',
       'http://www.tuulavintage.com/feed',
       'http://www.lovely-pepa.com/feed',
       'http://www.amlul.com/feed',
       'http://mariannan.costume.fi/feed']
       
def get_db_es(db_name):
    import pyes 
    conn = pyes.ES('http://dwalin-us-east-1.searchly.com/',
				basic_auth={'username': 'dev', 'password' : 'oqozmjudhxtbeagkjqzvj15tarseebyd'})
    return conn

def get_db(db_name):
    from pymongo import MongoClient
    uri = 'mongodb://user:passw0rd@oceanic.mongohq.com:10080/dev-itoutfits'
    client = MongoClient(uri)
    db = client[db_name]
    return db      

def blogsData(blogs):	

	d = feedparser.parse(blogs)
	db = get_db('dev-itoutfits')
	index_name = 'content'
	conn = get_db_es(index_name)
	
	for item in d['entries']:
		dic = {}		
		dic['titlePost'] = item.title.encode('utf-8').replace("\xe2\x80\x99","'")
		num =db.content.find({"titlePost":dic['titlePost']}).count()
		if num == 0:
			#print dic['titlePost'], num
			dic['rssLink'] = blogs
			dic['titleBlog'] = d['feed']['title'].encode('utf-8').replace("\xe2\x80\x99","'")
			dic['updated'] = d['feed']['updated'].encode('utf-8')		
			dic['descriptionBlog'] = d['feed']['description'].encode('utf-8').replace("\xe2\x80\x99","'")				
			dic['link'] = item.link.encode('utf-8')
			dic['date']=datetime.datetime.utcnow()
			#Detag content, define parsing rules for outfits and
			#set nltk process
			if item.content[0]:
				text = plaintext(item.content[0]['value'])
				dic['content'] = text.encode('utf-8').replace("\xe2\x80\x99","'").replace("\n"," ").replace(":"," ")
				dom = DOM(item.content)
				imagesUrl = []
				for e in dom('img'):
					imagesUrl.append(e.attributes.get('src','').encode('utf-8'))
				dic['images'] = imagesUrl
			elif item.description:
				text = plaintext(item.description)
				dic['content'] = text.encode('utf-8').replace("\xe2\x80\x99","'").replace("\n"," ").replace(":"," ")
				dom = DOM(item.description)
				imagesUrl = []
				for e in dom('img'):
					imagesUrl.append(e.attributes.get('src','').encode('utf-8'))
				dic['images'] = imagesUrl
			if item.published:
				dic['published'] = item.published.encode('utf-8')
			
			if "tags" in item:
				tags = []
				for tag in  item.tags:
					tags.append(tag.term.encode('utf-8'))
				dic['tags'] = tags	
			try:
				#print dic		
				db.content.update({"titlePost":dic['titlePost']},dic,upsert=True)
				#type_name="article"
				#conn.index(json.dumps(dic), index_name, type_name)
			except ValueError:
				pass

	#Add result to MongoDB
	#return dic

def main():	
	for blog in blogs:
		blogsData(blog)
		

if __name__ == '__main__':

	main()

