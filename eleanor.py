#!/usr/bin/env python
#coding: utf8 



'''
This script is being run on a RasberryPi in my house to interface with Nest, Google and a few other things to make a "smart(er) house".
'''

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree
import gdata.calendar.client
import gdata.calendar
import atom
import getopt
import sys
import string
import time
import re
import urllib2
from icalendar import Calendar, Event
import time
from datetime import date, datetime , timedelta
from time import gmtime, strftime
import subprocess
from subprocess import call
import MySQLdb
from optparse import OptionParser

sys.path.append(r'/home/pi/')
import nest


### SYSTEM VARIABLES ###
start_date = (date.today() - timedelta(days=0)).isoformat()
end_date = (date.today() + timedelta(days=1)).isoformat()
day_check = int(subprocess.check_output("date '+%u'", shell=True))
hour = int(strftime("%k"))
current_mysql_time = strftime('%Y-%m-%d %H:%M:%S')
mikey = '18327263821'            
        
### SPEECH ENGINES ###
def speak(text):
	print text
	call(["/home/pi/speak_british", text])
	cur.execute("""INSERT INTO eleanor_speak(`sent`, `text`) VALUES (%s ,%s)""", (current_mysql_time, text))
	db.commit()

def speak_british(text):
	print text
	call(["/home/pi/speak_british", text])
def speak_aussie(text):
	print text
	call(["/home/pi/speak_aussie", text])
def speak_german(text):
	print text
	call(["/home/pi/speak_de", text])
def speak_french(text):
	print text
	call(["/home/pi/speak_fr", text])
def speak_russian(text):
	print text
	call(["/home/pi/speak_ru", text])
def speak_spanish(text):
	print text
	call(["/home/pi/speak_es", text])
	
def sms(to, message):
	#to = '18327263821'
	#message = 'This is a text from Eleanor'
	gvapi = "gvapi -u mharrison.william@gmail.com -p [PASSWORD] -n " + to + " -m '" + message + "'"
	sms = subprocess.check_output(gvapi, shell=True)
	cur.execute("""INSERT INTO eleanor_sms(`sent`, `to`, `message`, `response`) VALUES (%s ,%s, %s, %s)""", (current_mysql_time, to, message, sms))
	db.commit()
	
	return sms
			    

### GOOGLE CALENDAR INTEGRATION ###
def DateRangeQuery(calendar_client, calendar, start_date, end_date):
    query = TryGoogleRequest(gdata.calendar.client.CalendarEventQuery)
    query.start_min = start_date
    query.start_max = end_date
    feed = TryGoogleRequest(calendar_client.GetCalendarEventFeed, q=query, uri=calendar)
    
    return feed
  
def TryGoogleRequest( fun, *args, **kwargs ):
    ret = None
    tries = 0
    while tries < 10:
        if tries in [4, 8]:
            time.sleep(120) # Sometimes it seems to error out if you hit it too fast
        try:
            ret = fun(*args, **kwargs)
            break
        except gdata.client.RedirectError as e:
            tries += 1
 
    if tries is 10:
        raise Exception('Repeatedly failed contacting Google Calendar services')
    
    return ret

def personal_events(start_date, end_date):
    cal_client = gdata.calendar.client.CalendarClient(source='Google-Calendar_Python-2.0')
    cal_client.ClientLogin("1403.delano.1@gmail.com", "[PASSWORD]", cal_client.source) # Probably a bad idea
     
    ical_feed = 'https://www.google.com/calendar/feeds/1403.delano.1%40gmail.com/public/basic'
    personal_calendar = cal_client.GetCalendarEventFeedUri(calendar='1403.delano.1@gmail.com',
                                                       visibility='private',
                                                       projection='full')
                                                        
    personal_feed = DateRangeQuery(cal_client, personal_calendar , start_date, end_date)
    personal_events = len(personal_feed.entry)

    personal_events_text =  "You have " + str(personal_events) + " events on your personal calendar occurring today"
    speak(personal_events_text)

    if personal_events != 0:
        personal_events_are = "Your personal events are "
        for i, a_calendar in enumerate(personal_feed.entry):
            if i != 0:
                personal_events_are += ' and '
                personal_events_are += ' ' + a_calendar.title.text
        speak(personal_events_are)


def work_events(start_date, end_date):
    cal_client = gdata.calendar.client.CalendarClient(source='Google-Calendar_Python-2.0')
    cal_client.ClientLogin("mwh5@rice.edu", "[PASSWORD]", cal_client.source) # Probably a bad idea
     
    ical_feed = 'http://www.google.com/calendar/feeds/mwh5%40rice.edu/public/basic'
    work_calendar = cal_client.GetCalendarEventFeedUri(calendar='mwh5@rice.edu',
                                                       visibility='private',
                                                       projection='full')
                                                       
    work_feed = DateRangeQuery(cal_client, work_calendar , start_date, end_date)
    work_events = len(work_feed.entry)
    
    work_events_text =  "You have " + str(work_events) + " events on your work calendar occurring today"
    speak(work_events_text)

    if work_events != 0:
        work_events_are = "Your work events are "
        for i, a_calendar in enumerate(work_feed.entry):
            if i != 0:
                work_events_are += ' and '
                work_events_are += ' ' + a_calendar.title.text
        speak(work_events_are)

## INSIDE TEMPERATURES ##
	
nest2 = subprocess.check_output("python nest.py --user='mikey_con@me.com' --password='[PASSWORD]' --index=1 show", shell=True)
nest3 = subprocess.check_output("python nest.py --user='mikey_con@me.com' --password='[PASSWORD]' --index=0 show", shell=True)

n2 = nest2.split('\n')
for n in n2:
    n = n.split(':')
    try:
        stat = n[0].replace('.', '')
        value = n[1].replace(' ', '')
    except:
        pass
    
    if stat == 'auto_away':
        auto_away2 = value
        if auto_away2 == '1':
            auto_away2=True
        else:
            auto_away2=False
    if stat == 'current_humidity':
        humidity2 = int(value)
    if stat == 'current_temperature':
        temp2 = float(value)
    if stat == 'target_temperature':
        target_temp2 = float(value)

n3 = nest3.split('\n')
for n in n3:
    n = n.split(':')
    try:
        stat = n[0].replace('.', '')
        value = n[1].replace(' ', '')
    except:
        pass
    
    if stat == 'auto_away':
        auto_away3 = value
        if auto_away3 == '1':
            auto_away3=True
        else:
            auto_away3=False
    if stat == 'current_humidity':
        humidity3 = int(value)
    if stat == 'current_temperature':
        temp3 = float(value)
    if stat == 'target_temperature':
        target_temp3 = float(value)        


temp2_update = "The temperature on floor two is %.1f degrees Celsius. The humidity is at %i percent" % (temp2, humidity2)
temp3_update = "The temperature on floor three is %.1f degrees Celsius and the humidity is at %i percent" % (temp3, humidity3)



### WEATHER ###

def weather():
    weatherC = subprocess.check_output("curl --silent 'http://xml.weather.yahoo.com/forecastrss?p=USTX0617&u=c' | grep -E '(Current Conditions:|C<BR)' | sed -e 's/Current Conditions://' -e 's/<br \/>//' -e 's/<b>//' -e 's/<\/b>//' -e 's/<BR \/>//' -e 's///' -e 's/<\/description>//'", shell=True)
    weatherF = subprocess.check_output("curl --silent 'http://xml.weather.yahoo.com/forecastrss?p=USTX0617&u=f' | grep -E '(Current Conditions:|F<BR)' | sed -e 's/Current Conditions://' -e 's/<br \/>//' -e 's/<b>//' -e 's/<\/b>//' -e 's/<BR \/>//' -e 's///' -e 's/<\/description>//'", shell=True)
    
    weatherC = weatherC.strip().split(",")
    conditionC = weatherC[0]
    tempC = weatherC[1].split(" ")
    tempC = tempC[1]
    
    weatherF = weatherF.strip().split(",")
    tempF = weatherF[1].split(" ")
    tempF = tempF[1]
    
    weather = "The weather is " + conditionC + " and it is " + tempC + " degrees Celsius, " + tempF + " degrees Fahrenheit"
    
    return weather

### DOWNLOAD MEDIA ###
def download(search):
	speak("I am searching for " + search)
	torrent = subprocess.check_output("download " + search, shell=True)
	torrent = torrent.strip().split(":")
	try:
		torrent= torrent[2].replace('"','').strip()
		if torrent == 'success':
			speak('I found it and I have begun the download on the media server!')
	except:
		speak('I was unable to find ' + search + " ,please try again")
		

### SECURITY VIOLATIONS/ WARNINGS ###
security_warning = "The security of the Delano will be maintained by any means necessary, no further violations will be tolerated."
harm_warning = "Continued operation may harm the system."
request_denied = "Eleanor can not handle your request at this time."

def emergency_test():
	emergency = "This is an emergency"
	speak(emergency)
	german_emergency = "Dies ist ein Notfall"
	speak_german(german_emergency)
	french_emergency = "il s'agit d'une urgence"
	speak_french(french_emergency)
	russian_emergency = "eto chrezvychaynaya situatsiya"
	speak_russian(russian_emergency)
	spanish_emergency = "esto es una emergencia"
	speak_spanish(spanish_emergency)

def alarm():
	print "Sounding emergency alarm!"
	call(["/home/pi/alarm"])
		
def breach():
	print "Breach detected in sector 7"
	call(["/home/pi/breach"])

### SYSTEM MONITORING ###
def pi_temp():
	temp = float(subprocess.check_output("/home/pi/temp.py", shell=True))
	if temp < 25:
		temp = "My core temperature is %.1f degrees, I am cool" % temp
	elif 25 <= temp < 35:
		temp = "My core temperature is %.1f degrees, I am just right" % temp
	elif 35 <= temp < 45:
		temp = "My core temperature is %.1f degrees, I am warm" % temp
	elif 45 <= temp < 55:
		temp = "My core temperature is %.1f degrees, I am hot" % temp
	elif temp > 55:
		temp = "My core temperature is %.1f degrees, I am dangerously hot" % temp
	else:
		temp = "I am receiving an invalid temperature reading from my core"
	
	return temp
	
#greeting = "Dea-lano Control Portal Speech Service"
def greeting(hour):
    if 5 <= hour < 12:
    	greeting = "Good morning"
    elif 12 <= hour < 17:
    	greeting = "Good afternoon"
    elif 17 <= hour < 23:
    	greeting = "Good evening"
    else:
    	greeting = "Excuse the late disruption"
    	
    return greeting

def date():
    date = subprocess.check_output("date '+%B %e'", shell=True).rstrip()
    date = "The date is " + date
    
    return date

def time():
    time = subprocess.check_output("date '+%k:%M %p'", shell=True).rstrip()
    time = "The time is " + time
    
    return time
	
def day():
    day = subprocess.check_output("date '+%A'", shell=True).rstrip()
    day = "Today is " + day
    
    return day


def create_parser():
   parser = OptionParser(usage="eleanor [options] command [command_options] [command_args]",
        description="Commands: eleanor, man",
        version="1")

   parser.add_option("-s", "--silent", dest="silent",
                     help="toggle silent mode", metavar="SILENT", default=False)


   return parser
   
def help():
    print "syntax: eleanor [options] command [command_args]"
    print
    print "commands: eleanor man"
    print "    eleanor       ... eleanor's main listening command"
    print "    man           ... man's main listening command"


def main():
    parser = create_parser()
    (opts, args) = parser.parse_args()

    if (len(args)==0) or (args[0]=="help"):
        help()
        sys.exit(-1)

	#might want to know if it's the weekend so we don't blare things when we want to sleep in
    if day_check >= 1 and day_check <= 5:
	    weekend=False
    else:
		weekend=True
	
    cmd = args[0]
    if opts.silent == 'True':
    	silent=True
        
    if (cmd == 'e'):
        if len(args)<2:
            speak("Eleanor requires more information to process your request")
            sys.exit(-1)
            
        do = args[1].lower()
        do = do.split()
    	
    	#download [movie|song|series|software]
    	if(do[0]=='download'):
    		media =  do[1:]
    		media = ', '.join(media).replace(',','')
    		download(media)
    	
    	elif(do[0]=='jurassic' ):
    		speak_british("Welcome to... Jurassic Park")
    		subprocess.check_output("mpg123 -q 'http://www.televisiontunes.com/themesongs/Jurassic%20Park.mp3'", shell=True)
    	
    	#set temperature to 25 degrees on floor [1|2|3]
    	elif(do[0]=='set' and do[1]=='temperature'):
    		try:
	    		temp = float(do[3])
	    		if(do[7]=='1' or do[7]=='one'):
	    			speak("The first floor currently requires manual temperature changes")
	    		elif(do[7]=='2' or do[7]=='two'):
	    			speak("I have set the temperature to %.1f degrees on the second floor" % temp)
	    		elif(do[7]=='3' or do[7]=='three'):
	    			speak("I have set the temperature to %.1f degrees on the third floor" % temp)
	    		else:
	    			speak("A valid floor and temperature must be given to set the temperature")
	    	except:
	    		speak("A valid floor and temperature must be given to set the temperature")


        #what is the [temperature|humidity|time|day|date|weather] [on floor [1|2|3]]
        elif(do[0]=='what' and do[1]=='is' and do[2]=='the'):
        	if(do[3]=='temperature'):
        		if(do[4]=='average'):
        			average = ((temp2 + temp3) / 2)
        			speak("The average house temperature is %.1f degrees Celsius" % average)
        		elif(do[6]=='1' or do[6]=='one'):
        			speak("The first floor temperature sensors are currently unavailable")
        		elif(do[6]=='2' or do[6]=='two'):
        			speak("The temperature is %.1f degrees Celsius on floor two" % temp2)
        		elif(do[6]=='3' or do[6]=='three'):
        			speak("The temperature is %.1f degrees Celsius on floor three" % temp3)
        		else:
        			speak(temp2_update)
        			speak(temp3_update)
        	elif(do[3]=='humidity'):
        		try:
	        		if(do[4]=='average'):
	        			average = ((humidity2 + humidity3) / 2)
	        			speak("The average house humidity is %i percent" % average)
	        		elif(do[6]=='1'):
	        			speak("The first floor humidity sensors are currently unavailable")
	        		elif(do[6]=='2'):
	        			speak("The humidity is %i percent on floor two" % humidity2)
	        		elif(do[6]=='3'):
	        			speak("The humidity is %i percent on floor three" % humidity3)
	        		else:
        				speak(temp2_update)
        				speak(temp3_update)
        		except:
        			speak(temp2_update)
        			speak(temp3_update)        
        				
        	elif(do[3]=='time'):
        		speak(greeting(hour))
        		speak(time())
        	elif(do[3]=='day'):
        		speak(day())
        	elif(do[3]=='date'):
        		speak(date())
        	elif(do[3]=='weather'):
        		speak(weather())

        elif(do[0]=='are' and do[1]=='you' and (do[2]=='hot' or do[2]=='cold')):
        	speak(pi_temp())
        	sms(mikey, pi_temp())

    	#sound the alarm
    	elif(do[0]=='emergency'):
    		sms(mikey, "Emergency protocol initiated")
    		breach()
    		emergency_test()
    		alarm()
    		
    		
    	else:
    		speak("Eleanor does not understand " + str(do))
    		
    else:
        print "misunderstood command:", cmd
        print "run 'eleanor.py help' for help"

if __name__=="__main__":
   main()
