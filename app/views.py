# -*- coding: utf-8 -*-
from flask import render_template,request
from flask import jsonify
from app import app
import json, time, random, re, time

def get_db(db_name):
    from pymongo import MongoClient
    uri = 'mongodb://user:passw0rd@oceanic.mongohq.com:10080/dev-itoutfits'
    client = MongoClient(uri)
    db = client[db_name]
    return db

def searchES(query):
    import pyes 
    conn = pyes.ES('http://dwalin-us-east-1.searchly.com/',
                basic_auth={'username': 'dev', 'password' : 'oqozmjudhxtbeagkjqzvj15tarseebyd'})
    q = pyes.StringQuery(query, default_operator="AND")
    result = conn.search(query=q, indices="content")
    data=[]
    for r in result:
        data.append(r)
    return data  

@app.route('/')
def index():
    return render_template("mainpage.html",
                            title = "Welcome to the latest fashion bloggers trends",
                            card=[])

@app.route('/about')
def about():
    return render_template("about.html",
                            title = "About",
                            card=[])

@app.route("/search/<tag>", methods = ['GET', 'POST'])
@app.route("/search", methods = ['GET', 'POST'])
def search(tag=None):
    if request.args.get('text'):
        search_term = request.args.get('text')
    elif tag:
        search_term = tag
    else:
        search_term = "outfits"
    db = get_db('dev-itoutfits')
    query = {"titleBlog":search_term}
    mongoData = db.content.find(query).count()
    if mongoData > 0:
        output = db.content.find(query)        
    else:
        mongoData =  db.command('text', 'content', search=search_term)
        output = []
        for item in mongoData['results']:
            output.append(item['obj'])     
    #else:
    #    output = searchES(search_term)
    return render_template("search.html",
                            title = search_term,                            
                            data = output,
                            card=output[0])   

@app.route("/post/<titleBlogUrl>/<titlePostUrl>", methods = ['GET', 'POST'])
def post(titleBlogUrl,titlePostUrl):
    search_term = titlePostUrl
    db = get_db('dev-itoutfits')
    query = {"titlePostUrl":search_term}
    mongoData = db.content.find(query).count()
    if mongoData > 0:        
        output = db.content.find(query)
        titlePost = output[0]['titleBlog']
        imagesUrl = output[0]['images']         
    return render_template("post.html",
                            title = output[0]['titlePost'],
                            post =  titlePost,                            
                            data = output[0],
                            card= output[0],                           
                            dataImages = imagesUrl )   

@app.route("/latestoutfits", methods = ['GET', 'POST'])
def latest():    
    db = get_db('dev-itoutfits')    
    output = db.content.find().sort('date',-1).limit(21)
    return render_template("search.html",
                            title = 'Latest Outfits',                                                       
                            data = output,
                            card= output[0])   

@app.route('/analytics')
def analytics(): 
    output= getNews.wordCount()
    output2 = getNews.getDataAnalysis()
    now = time.strftime("%c")
    return render_template("analytics.html",                            
                            entities = output,
                            data = output2,
                            now= now)

@app.route('/sitemap.xml')
def sitemap():
    url_root = request.url_root[:-1]
    rules = app.url_map.iter_rules()
    return render_template('sitemap.xml', url_root=url_root, rules=rules)