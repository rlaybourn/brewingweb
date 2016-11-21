##
##   display environment variables in mod_wsgi - shows if wsgi, flask etc is working
##

from flask import Flask, request, make_response,render_template,jsonify
import sys
import gviz_api
import csv
import MySQLdb as mdb
import datetime
import json
import syslog

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
            UserMixin, RoleMixin, login_required

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SECURITY_POST_LOGOUT_VIEW'] = 'thelog'

# Create database connection object
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    user_datastore.create_user(email='earlgrey1979@gmail.com', password='password')
    db.session.commit()

def get_last_row(csv_filename):
    with open(csv_filename,'rb') as f:
        reader = csv.reader(f)
        lastline = reader.next()
        for line in reader:
            lastline = line
        return lastline

@app.route('/new',methods=['POST','GET'])
def newNode():
	try:
		theIp = request.args.get("Ip")
		theName = request.args.get("name")
		theSetpoint = request.args.get("setp")
		if((theIp == None) or (theName == None)):
			return jsonify(status="nodata") 
		if(theSetpoint == None):
			theSetpoint = 15.0
	
		try:
       	        	con = mdb.connect('localhost','root','banaka','brewing')
 	             	cur = con.cursor()
                	cur.execute("select t1.node_id+1 as next from nodes as t1 left join nodes as t2 on t1.node_id+1 = t2.node_id where t2.node_id is null order by t1.node_id limit 1" )
                        nextnum = cur.fetchone()[0]
                        cur.execute("insert into nodes (node_id,Ip,name,setpoint) values (%s,\"%s\",\"%s\",%s)" %(nextnum,theIp,theName,theSetpoint))
                	cur.close()
                        con.commit()
                	con.close()
		except Exception as e:
			return str(e)#jsonify(status="dbp")
		return jsonify(status="ok",nextid=nextnum)
	except Exception as e:
		return str(e)
		


@app.route('/update',methods=['POST','GET'])
def updateNode():
        try:
                whichNode = request.args.get("node")
                newIp = request.args.get("ip")
                newName = request.args.get("name")
                newTemp = request.args.get("temp")
                if(whichNode == None) or (newIp == None) or (newName == None):
                        return jsonify(status="error",node= whichNode, IP = newIp) 
        except Exception as e:
                return str(e)
        try:
            if(newTemp == None):
                con = mdb.connect('localhost','root','banaka','brewing')
                cur = con.cursor()
                cur.execute("select * from nodes where node_id = 1" )
                cur.execute("update nodes set ip = \"%s\",name = \"%s\" where node_id = %s" % (newIp , newName,whichNode))
                cur.close()
                con.commit()
                con.close()
            else:
                con = mdb.connect('localhost','root','banaka','brewing')
                cur = con.cursor()
                cur.execute("select * from nodes where node_id = 1" )
                cur.execute("update nodes set ip = \"%s\",name = \"%s\",setpoint = \"%s\" where node_id = %s" % (newIp , newName,newTemp,whichNode))
                cur.close()
                con.commit()
                con.close()
        except Exception as e:
                return str(e)#jsonify(status="dbp")
        return jsonify(status="ok",node= whichNode, IP = newIp)

@app.route('/start',methods=['POST','GET'])
def startBrew():
    try:
        whichNode = request.args.get("node")
        if(whichNode == None):
            return jsonify(status="error",node= whichNode)
    except Exception as e:
        return str(e)

    try:
        con = mdb.connect('localhost','root','banaka','brewing')
        cur = con.cursor()
        cur.execute("update nodes set brewstart = now() where node_id = %s" % whichNode)
        cur.close()
        con.commit()
        con.close()
    except Exception as e:
        return str(e)#jsonify(status="dbp")

    return jsonify(status="ok",node= whichNode)



@app.route('/delete',methods=['POST','GET'])
def delNode():
	try:
		whichNode = request.args.get("node")
		if(whichNode == None):
			return "non node"
	except Exception as e:
		return str(e)
	try:
		con = mdb.connect('localhost','root','banaka','brewing')
		cur = con.cursor()
		cur.execute("delete from nodes where node_id = %s" % whichNode )
		cur.close()
                con.commit()
		con.close()
	except Exception as e:
		return str(e)#jsonify(status="dbp")
#	except Exception as e:
#		return str(e)
	return jsonify(status="ok")

@app.route('/temptest',methods=['POST','GET'])
def templating():
	try:
		return render_template('fortemp.html',test=['rich' ,'glyn','mom' ,'dad'])
	except Exception as e:
		return str(e);


@app.route('/collect',methods=['POST','GET'])
def getjson():
	try:
		content = request.json
		return jsonify(status="ok",time = str(datetime.datetime.now()))
	except Exception as e:
		return str(e)
@app.route('/ndata',methods=['POST','GET'])
def getNdata():
	try:
                whichNode = request.args.get("node")
                if(whichNode == None):
                        whichNode = 1
                con = mdb.connect('localhost','root','banaka','brewing')
                cur = con.cursor()
                cur.execute("select node_id,setpoint,name,ip,datediff( now() , brewstart) from nodes where node_id = %d" % int(whichNode))
		res = cur.fetchone()
		cur.close()
		con.close()
		return jsonify(Id = res[0],IP = res[3],name = res[2],setp = res[1],brewfor = res[4])
	except Exception as e:
		return str(e)
@app.route("/deldata",methods=['POST','GET'])
def delSdata():
    try:
        whichItem =  request.args.get("uid")
        con = mdb.connect('localhost','root','banaka','brewing')
        cur = con.cursor()
        cur.execute("delete from schedules where uid = %s" % whichItem)
        cur.commit()
        cur.close()
        return jsonify(status = "ok")
    except Exception as e:
        return jsonify(status = str(e))

@app.route('/mnodes',methods=['POST','GET'])
@login_required
def mNodes():
	try:
                con = mdb.connect('localhost','root','banaka','brewing')
                cur = con.cursor()
                cur.execute("select node_id,setpoint,name,ip,switches,datediff( now() , brewstart) from nodes order by node_id")
                res = cur.fetchall()
                cur.close()
                con.close()
		return render_template('mnodes.html',list=res)
	except Exception as e:
		return str(e)

@app.route('/addaction',methods=['POST','GET'])
def Action():
        whichNode = request.args.get("node")
        days = request.args.get("days")
        hours = request.args.get("hours")
        temp = request.args.get("temp")
        try:
            con = mdb.connect('localhost','root','banaka','brewing')
            cur = con.cursor()
            cur.execute("insert into schedules (node_id,acttime,newtemperature,completed) values (%s,now() + interval %s day + interval %s hour,\"%s\",false)" % (whichNode,days,hours,temp))
            cur.close()
            con.commit()
            con.close()
            return jsonify(Id=whichNode,status='ok')
        except Exception as e:
            return jsonify(Id=whichNode,status="insert into schedules (node_id,acttime,newtemperature) values (%s,now() + interval %s day,\"%s\")" % (whichNode,days,temp))
 

@app.route('/about',methods=['POST','GET'])
def theAbout():
        try:
                con = mdb.connect('localhost','root','banaka','brewing')
                cur = con.cursor()
                cur.execute("select schedules.node_id,nodes.name,acttime,newtemperature,uid from schedules inner join nodes on schedules.node_id = nodes.node_id where schedules.completed = false order by schedules.acttime")
                res = cur.fetchall()
                cur.execute("select node_id, name from nodes")
                nodelist = cur.fetchall()
                cur.close()
                con.close()
                #nodelist = [1,2]
                thelist = list(nodelist)
                thelist.insert(0,[0,"none"])
                return render_template('about.html',list=res,allnodes=thelist)
        except Exception as e:
                return str(e)

@app.route('/mob',methods=['POST','GET'])
def theMob():
        try:
                return render_template('mobchart.html')
        except Exception as e:
                return str(e)

@app.route('/logout',methods=['POST','GET'])
def logout():
    try:
        flask_security.utils.logout_user()
        return jsonify(status = "gone")
    except Exception as e:
        return str(e);


@app.route('/thelog',methods=['POST','GET'])
@login_required
def thelogout():
	try:
                con = mdb.connect('localhost','root','banaka','brewing')
                cur = con.cursor()
                cur.execute("select node_id,setpoint,name,ip,switches,datediff( now() , brewstart) from nodes order by node_id")
                res = cur.fetchall()
                cur.close()
                con.close()               
		return render_template('expchart.html',list=res)
	except Exception as e:
		return str(e)


@app.route('/raw', methods=['POST','GET'])
def rawdata():
	try:
		whichNode = request.args.get("node")
		if(whichNode == None):
			whichNode = 1
		con = mdb.connect('localhost','root','banaka','brewing')
		cur = con.cursor()
		cur.execute("select wort,ambient,setpoint from templogs where node_id = %d order by thetime desc limit 1" % int(whichNode))
		res = cur.fetchone()
		cur.close()
		con.close()
		#list = get_last_row('/var/www/log.csv')
		#return jsonify(wort = list[1],ambient = list[2],setpoint = list[3])
		return jsonify(wort = res[0],ambient = res[1],setpoint = res[2])
	except Exception as e:
		return str(e)
@app.route('/nodelist',methods=['POST','GET'])
def nodeList():
    try:
        con = mdb.connect('localhost','root','banaka','brewing')
        cur = con.cursor()
        cur.execute("select node_id,setpoint,name,ip,switches,datediff( now() , brewstart) from nodes order by node_id")
        res = cur.fetchall()
        cur.close()
        con.close()
        thelist = []
        for item in res:
            thelist.append({'ID' : item[0],'NAME' : item[2],'SETPOINT' : item[1], 'IP' : item[3], 'DURATION' : item[5]})
        return jsonify(nodes = thelist)
    except Exception as e:
        return str(e)

@app.route('/set', methods=['POST','GET'])
def set():
	wated = float(request.args.get('temp'))
	wated = wated
	whichNode = request.args.get("node")
	if(whichNode == None):
		whichNode = 1

	try:
	        con = mdb.connect('localhost','root','banaka','brewing')
	        cur = con.cursor()
		cur.execute("update nodes set setpoint = %f where node_id = %d" %(float(wated),int(whichNode)))
		con.commit()
		con.close()
        	return jsonify(stat = "success",tmp = str(wated))
	except Exception as e:
		return jsonify(stat = str(e),tmp = str(0))
	
@app.route('/data', methods=['POST', 'GET'])
def outdata():
	period = request.args.get("days")
	whichNode = request.args.get("node")
	
	if(period == None):
		period = 2
	if(whichNode == None):
		whichNode = 1

	try:		
        	con = mdb.connect('localhost','root','banaka','brewing')
        	cur = con.cursor()
        	cur.execute("select wort,ambient,date_format(thetime,'%i'), date_format(thetime,'%H'), date_format(thetime,'%e'),setpoint ,date_format(thetime,'%m'),inside from templogs where thetime > (CURDATE() - interval " + str(period) +" day) and node_id = "+str(whichNode))
        	res = cur.fetchall()
        	cur.close()
        	con.close()
	except Exception as e:
		return "ell well" + str(e) 
	readingsList = []
	try:
		for row in res:
			numerified = [datetime.datetime(2016,int(row[6]),int(row[4]),int(row[3]),int(row[2])),float(row[0]),float(row[1]),float(row[5]),float(row[7])]
			readingsList.append(numerified)
				
		description = [("minutes","datetime"),("wort","number"),("ambient","number"),("setp","number"),("inside","number")]

		data_table = gviz_api.DataTable(description)
		data_table.LoadData(readingsList)
		return data_table.ToJSon(columns_order=("minutes","wort","ambient","setp","inside"))
	except Exception as e:
		return "some kidn of error %s" % str(e)



@app.route('/', methods=['POST', 'GET'])
def indexApp():
    try:
        env = request.environ
        output = 'Hello World! with a little change<hr>'
	#return render_template('hello.html', name="rich")
        return output
    except:
        import traceback
        response = make_response(WSerrorTextHTML(traceback.format_exc()))
        response.headers['Content-Type'] = 'text/html'
        return response

    return "<p>something wrong!</p>"

if __name__ == "__main__":
    #application.debug = True
    app.run(debug=True,host='0.0.0.0')

