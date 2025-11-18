from flask import Flask, render_template,request,flash,redirect,url_for

from find_pair import find_stocks_that_move_together 

app = Flask(__name__, static_folder='static')

@app.route("/",methods=['GET','POST'])
def find_pair():
    if request.method == "POST" :
        find_stocks_that_move_together()
        return render_template("find_pair.html")
    return render_template("find_pair.html")