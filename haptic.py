import os
import sys
import socket
import urllib
import math
import json
import csv
from pprint import pprint
import time


conf_file="haptic.conf"

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
			response[row[0]]={"start": float(row[1]), 'duration': map(float, row[2:])}
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
	    print( "couldn't find file: %s" % (s))



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
	time.sleep(config["sleep-time-in-seconds"])


def load_files ():
	reload_sensitive(conf_file, parse_conf)
	if len(config) > 0:
		reload_sensitive(config['buzzers-path'], parse_buzzers)	



def fetch_json_url (url):
	response = urllib.urlopen(url)
	return json.loads(response.read())
	


def when_playing (f):
	player_data=fetch_json_url( config["player-data-url"])
	if "file" in player_data and player_data["file"] in files_i_watch_for:
		f(player_data)




def figure_future_buzz (player_data):
	where_we_are = player_data["position_millis"]/1000.0
	started_playing_at = time.time()-where_we_are
	buzz_point_in_video = files_i_watch_for[player_data["file"]]["start"] / 1000.0
	return started_playing_at + buzz_point_in_video 



def buzz (duration):
	print("buzzing for %s" % (duration / 1000.0))
	time.sleep(duration / 1000.0)
	


def do_buzzes(durations):
	# print(durations)
	for i in range(0, int(math.ceil(len(durations) / 2.0))):
		buzz(durations[i*2])
		if 1+i*2 < len(durations):
			print("waiting for %s" % (durations[i*2 + 1]/ 1000.0 ))
			time.sleep(durations[i*2 + 1] / 1000.0)
	print("done")


def execute_buzz(player_data):
	buzz_at = figure_future_buzz(player_data)
	time_till_buzz = buzz_at - time.time()

	durations = files_i_watch_for[player_data["file"]]["duration"]


	if time_till_buzz > 0.0:
		
		# the buzz is in the future
		print("will buzz in %s" % (time_till_buzz))

		#sleep until it's time to buzz
		time.sleep(time_till_buzz)

		do_buzzes(durations)







def just_found_file(player_data):
	buzz_at = figure_future_buzz(player_data)
	time_till_buzz = buzz_at - time.time()

	if time_till_buzz > 0.0:
		# the buzz is in the future
		print("will buzz in %s" % (time_till_buzz))

		print("durations will be %s" % (files_i_watch_for[player_data["file"]]["duration"]))


		#sleep until we're 10 seconds out
		time.sleep(time_till_buzz - 10)

		when_playing(execute_buzz)




def process_anything_running ():
	when_playing(just_found_file)


def runit ():
	load_files()
	process_anything_running()
	wait()



print("Starting haptic listener for %s" % (socket.gethostname()))


while True:
	runit()
