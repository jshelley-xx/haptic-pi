import os
import sys
import socket
import urllib
import json
import csv
from pprint import pprint
import time


conf_file="haptic.conf"

global config
config={}
last_loaded={}


files_i_watch_for = {}


def load_file(s):
	return open(s).read()



def load_csv(s):
	with open(s, 'rb') as csvfile:
		r = csv.reader(csvfile)
		response={}
		for row in r:
			response[row[0]]={"start": row[1], 'duration': row[2]}
		return response



def load_json_file (s):
		tmp_data=load_file(s)
		as_json = json.loads(tmp_data)
		return as_json



def need_to_reload (s):
	if os.path.isfile(s):
	    last_modified_date = os.path.getmtime(s)
	    return (last_modified_date > ( (last_loaded[s] if s in last_loaded else -1) + 5 ))
	else:
	    print( "couldn't find file: %s" (s))



def nvl (d, k, dflt):
	if k in d:
		return d[k]
	else:
		return d[dflt]


def reload_sensitive (s, f):
	if need_to_reload(s):
		try:
			f()
			global last_loaded
			last_loaded[s]=time.time()
			print("loaded file %s at %s" % (s, last_loaded[conf_file]))
			return True
		except Exception as e:
			print("unable to load file : %s %s" % (s, str(e)))
	return False



def parse_conf():
	global config
	config = nvl(load_json_file(conf_file), socket.gethostname(), "default")
	# pprint(config)



def parse_buzzers():
	global files_i_watch_for
	files_i_watch_for = load_csv(config["buzzers-path"])
	# pprint(files_i_watch_for)




def wait ():
	time.sleep(3)




def load_files ():
	reload_sensitive(conf_file, parse_conf)
	if len(config) > 0:
		reload_sensitive(config['buzzers-path'], parse_buzzers)	



def fetch_json_url (url):
	response = urllib.urlopen(url)
	return json.loads(response.read())
	


def process_anything_running ():
	player_data=fetch_json_url( config["player-data-url"])
	if "file" in player_data and player_data["file"] in files_i_watch_for:
		position=player_data["position_millis"] / 1000;
		pprint(position)
	# pprint(player_data)


def runit ():
	load_files()
	process_anything_running()
	wait()



print("Starting haptic listener for %s" % (socket.gethostname()))


while True:
	runit()
