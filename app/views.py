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
                            title = "Welcome")

@app.route('/about')
def about():
    return render_template("about.html",
                            title = "About")

@app.route("/search", methods = ['GET', 'POST'])
def search():
    if request.method =="POST":
        search_term = request.form['text']
    else:
        search_term = "outfits"
    db = get_db('dev-itoutfits')
    query = {"titleBlog":search_term}
    #mongoData = db.content.find(query).count()
    #mongoData = db.command('text', 'content', search=search_term).count()
    #if mongoData > 0:
        #mongoData = db.content.runCommand("text",{search:"Tuula", sort:"date"})
        #db.command('text', 'content', search=search_term)
    mongoData =  db.command('text', 'content', search=search_term)
    output = []
    for item in mongoData['results']:
        output.append(item['obj'])
    #output = db.content.find(query)        
    #else:
    #    output = searchES(search_term)
    return render_template("search.html",
                            title = search_term,                            
                            data = output)    

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