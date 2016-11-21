import time
import MySQLdb as mdb
import urllib2
import json

theNode = 1
setpoint = float(16.0)
con = mdb.connect('localhost','root','banaka','brewing')
cur = con.cursor()


try:
    cur.execute("select setpoint,ip,node_id from nodes") #pick current setpoing out of node settings table
    reses = cur.fetchall()
    cur.execute("select node_id,acttime,newtemperature,uid from schedules where acttime < now() and completed = false")
    actions =  cur.fetchall()
except Exception as e:
    print str(e)
for res in reses:
    try:
	setpoint = float(res[0])
	IpAddress = res[1]
	theNode = res[2]
	print IpAddress
	print theNode
	req = urllib2.Request("http://%s/raw?setpoint=%f" %(IpAddress,setpoint))
	opener = urllib2.build_opener()
	f = opener.open(req)
	rcjson = json.loads(f.read())
	print rcjson["wort"]
	print rcjson["setp"]
        print rcjson["inside"]
	cur.execute("insert into templogs (wort,inside,ambient,thetime,node_id,setpoint) values (%f,%f,%f,now(),%d,%f)" % (float(rcjson["wort"]),float(rcjson["inside"]),float(rcjson["amb"]),theNode,setpoint))
	con.commit()

    except Exception as e:
        print( "oops")
	print str(e)
	    #exit()

for item in actions:
    thenode = item[0]
    time = item[1]
    temperature = item[2]
    itemid = item[3]
    cur.execute("update nodes set setpoint = %s where node_id = %s" %(temperature,thenode))
    cur.execute("update schedules set completed = true where uid = %s" %(itemid))
    print "change to node %s %s at time %s" %(thenode,time,temperature)
    con.commit()

#cur.execute("insert into templogs (wort,ambient,thetime,node_id,setpoint) values (%f,%f,now(),%d,%f)" % (float(json["wort"]),float(json["amb"]),theNode,setpoint))
#con.commit()
con.close()
