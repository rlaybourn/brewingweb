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

app = Flask(__name__)

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
                	cur.execute("select * from nodes where node_id = 1" )
                	cur.close()
                	con.close()
		except Exception as e:
			return str(e)#jsonify(status="dbp")
		return jsonify(status="ok")
	except Exception as e:
		return str(e)
		


@app.route('/update',methods=['POST','GET'])
def updateNode():
        try:
                whichNode = request.args.get("node")
                if(whichNode == None):
                        return "non node"
        except Exception as e:
                return str(e)
        try:
                con = mdb.connect('localhost','root','banaka','brewing')
                cur = con.cursor()
                cur.execute("select * from nodes where node_id = 1" )
                cur.close()
                con.close()
        except Exception as e:
                return str(e)#jsonify(status="dbp")
#       except Exception as e:
#               return str(e)
        return jsonify(status="ok")


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
		cur.execute("select * from nodes where node_id = 1" )
		cur.close()
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
                cur.execute("select * from nodes where node_id = %d" % int(whichNode))
		res = cur.fetchone()
		cur.close()
		con.close()
		return jsonify(Id = res[0],IP = res[3],name = res[2],setp = res[1])
	except Exception as e:
		return str(e)
@app.route('/mnodes',methods=['POST','GET'])
def mNodes():
	try:
                con = mdb.connect('localhost','root','banaka','brewing')
                cur = con.cursor()
                cur.execute("select * from nodes")
                res = cur.fetchall()
                cur.close()
                con.close()
		return render_template('mnodes.html',list=res)
	except Exception as e:
		return str(e)

@app.route('/about',methods=['POST','GET'])
def theAbout():
        try:
                return render_template('about.html')
        except Exception as e:
                return str(e)

@app.route('/mob',methods=['POST','GET'])
def theMob():
        try:
                return render_template('mobchart.html')
        except Exception as e:
                return str(e)


@app.route('/thelog',methods=['POST','GET'])
def thelogout():
	try:
		return render_template('expchart.html', name="rich")
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
        	cur.execute("select wort,ambient,date_format(thetime,'%i'), date_format(thetime,'%H'), date_format(thetime,'%e'),setpoint ,date_format(thetime,'%m')from templogs where thetime > (CURDATE() - interval " + str(period) +" day) and node_id = "+str(whichNode))
        	res = cur.fetchall()
        	cur.close()
        	con.close()
	except Exception as e:
		return "ell well" + str(e) 
	readingsList = []
	try:
		for row in res:
			numerified = [datetime.datetime(2016,int(row[6]),int(row[4]),int(row[3]),int(row[2])),float(row[0]),float(row[1]),float(row[5])]
			readingsList.append(numerified)
				
		description = [("minutes","datetime"),("wort","number"),("ambient","number"),("setp","number")]

		data_table = gviz_api.DataTable(description)
		data_table.LoadData(readingsList)
		return data_table.ToJSon(columns_order=("minutes","wort","ambient","setp"))
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

