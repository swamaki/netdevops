'''
Would anyone here be interested in a script I've written?

A co-worker of mine had asked me if we could strip the CPS(connections per second) in show session info as the OID for CPS is just a table of the individual TCP/UDP/other and connections per second isn't a pollable/reportable metric. We know we can view a graph of the CPS in Panorama, but for alerting and other monitoring applications we use, this doesn't work, and it's not exportable.

So I used the XML API and call the show session info and I then use regex to strip out the content of the HTTP GET, use a timestamp module, append both of those two a list and then write/append to a CSV, and then set that function to execute every X times in schedule(you can set whatever frequency you want in the scheduler)

From there I'm either going to present it in Django, or import it as a custom HTML resource in our Orion NPM.

I've scoured thwack to see if I could write directly to our Orion DB and then just query whatever I have written to the tables through Orion and build the metric that way.

https://www.reddit.com/r/networking/comments/ih0ukl/palo_alto_python_script/

'''

import datetime
import time
import re
import schedule
import os
import urllib3
from csv import writer
import requests
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings()

#ignores cert errors
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#function of the api call
def api_call_csv():

    #api command to be sent defined
    command = "<show><session><info></info></session></show>"
    
    #calls api key from locally stored env variable
    api_key_inet = os.environ.get('API_KEYINET')
    
    #calls API hostname from locally stored env variable
    api_host_inet = os.environ.get('API_HOSTINET')


    #executes XML API call using request module, and arugments above
    req = requests.get('https://%s/api/?type=op&cmd=%s&key=%s'%(api_host_inet,command,api_key_inet), verify=False)

    #api call content block decoding xml to UTF
    api = req.content.decode('UTF-8')
    
    #create REGEX search object to filter CPS and any digit inside
    prog = re.compile("<cps>\d*</cps>")
    
    #findall matches for RegEX object
    result = prog.findall(api)
    
    #convert Regex Matches to string
    rsstg = ''.join(result)
    
    #strip first XML tag
    strip_first = re.sub(r"<cps>", '', rsstg)
    
    #strip XML tail
    strip_out = re.sub(r"</cps>", '', strip_first)


    #change working directory of where CSV needs to be created
    os.chdir(###insertCSVpath###)

    #define time in float
    ts = time.time()
    
    #format timestamp from float to YEAR-MONTH-DAY, HH:MM:SS
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    #put TIMESTAMP string into list, along with connections per second output
    final = [st, strip_out]



#function to open/append CSV file with list of time/CPS
    def append_list_as_row(file_name, list_of_elem):
       
        #open file in append mode
        with open(file_name, 'a+', newline='') as write_obj:
            # create a writer object from csv module
            csv_writer = writer(write_obj)
            #add contents of list as last row in csv file
            csv_writer.writerow(list_of_elem)
            #close csv when done writing        
            write_obj.close()

    append_list_as_row('###CSVfilename###', final)

"""call the API function and schedule to execute every 10 seconds, 
change to whatever interval you need """ 
 
schedule.every(10).seconds.do(api_call_csv)

while 1:
        schedule.run_pending()
        time.sleep(1)


'''
you'll need to store your private key, hostname as environment variables this method or you can just replace the api_key_inet and api_host_inet variables with the respective strings for testing, but i don't recommend storing them in you .py file

Go easy on me, I'm still pretty new at python, but maybe this will help a few others.

**We, unfortunately, don't have ORION SAM which can't execute scripts of most languages to pull in information, I wish NPM would do the same.

Time	CPS	
8/25/2020 2:16:00 PM	632	
8/25/2020 2:16:10 PM	416	

================================================

Nice work! I find working with Palo's API a bit frustrating myself. The docs aren't great, and XML isn't too friendly to work with as compared to JSON. Although I completely understand that the config is written in XML so naturally an XML API is what is used...

Palo's RESTFUL API is way better because you can return data in JSON, but it is quite limited. I find myself having to turn on debug cli on in the Palo CLI and get an XML operation cmd from that. Really tedious...



Just a little constructive feedback - you shouldn't be using regex to parse XML:

    prog = re.compile("<cps>\d*</cps>")

Instead, you should be parsing the XML into a python object ( a dictionary), and then get the CPS based on the key. I.E. it will probably be something like this :

    import xmltodict
    request_result = requests("GET", url...)
    result_dict = xmltodict.parse(request_result.text)
    cps = result_dict['response']['cps'] #this is just a guess. Print out the result_dict to take a look at how it is formatted to figure out how to key into 'cps'


Now you are working with the data more properly, and don't need to do things like this to get rid of the XML tags:

    #strip first XML tag
    strip_first = re.sub(r"<cps>", '', rsstg)
    
    #strip XML tail
    strip_out = re.sub(r"</cps>", '', strip_first)

This will definitely help you if you continue to use the Palo XML API in the future.

================================================
that worked perfectly!
for this xml tree i had to do the following

    result_dict = xmltodict.parse(req.text)
    cps = result_dict['response']['result']['cps']
    OrderedDict([('response',
                OrderedDict([('@status', 'success'),
                            ('result',
                                OrderedDict([('tmo-sctpshutdown', '###'),
                                ###redacted###
                                ('cps', '520'),
works absolutely gloriously

'''