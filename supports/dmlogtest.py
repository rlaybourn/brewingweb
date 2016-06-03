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

#print json["wort"]
#print json["setp"]
	

#cur.execute("insert into templogs (wort,ambient,thetime,node_id,setpoint) values (%f,%f,now(),%d,%f)" % (float(json["wort"]),float(json["amb"]),theNode,setpoint))
#con.commit()
con.close()
