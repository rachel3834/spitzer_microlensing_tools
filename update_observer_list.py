#!/usr/bin/env python
###############################################################################
#     	      	      	UPDATE OBSERVER LIST
#
# Purpose:
#    To programmatically register or deregister that a given observer is observing 
#    a given target
# Author:
#    Rachel Street @ LCOGT
###############################################################################

###############################
# IMPORTED MODULES
from os import path
from sys import argv
from urllib import urlencode
import urllib2
import cookielib
import getpass
import target_class
import swapname_public

###############################
# DECLARED STATEMENTS
help_text = '''                     UPDATE OBSERVER LIST

This script is designed to programmatically register or deregister that a given observer is observing 
a given target with the Spitzer online target system.  

Operation:
    From the commandline, type:
    > python update_observer_list.py [inputs]
    
Inputs (all mandatory):
    -mode         can be either "add" or "remove"
    -observer_id  should be one of the recognised observers registered with the online portal.
    -target_id    should be the shorthand name of a target in the Spitzer target list. 
    -user [ID] -pass [code]  Requires both -user and -pass arguments to be given, followed by
              the respective access codes.  These will be prompted for if not given. 
'''

version = 'update_observer_list_v1.0'

################################
# DRIVER FUNCTION
def update_observer_list(params):
    '''Function to add or remove (according to parameter flag), observer_id from the list of observers 
    in the Spitzer online interface for the targets listed in object_list.  
    
    It takes as input a dictionary with the following parameters:
    params = { 'userID': <given or prompted for>,
               'password': <given or prompted for>,
	       'observer_id': <given, must be recognized by Spitzer interface otherwise no action taken>,
	       'object_list': <given, a list of target names in short-hand format, which 
	                      are required to be present in the target list.  If not present, 
			      no action will be taken.>
	       'mode': <given> Either "add" or "remove" as a lower-case string. 
	     }
    '''

    # Initialize response message, returned in all cases:
    user_info = []
    update_script_url = 'http://robonet.lcogt.net/cgi-bin/private/cgiwrap/robouser/update_observer_list.cgi'
    
    # Compose authentication details if not already available:
    if params['userID'] == None: params['userID'] = raw_input('Username: ')
    if params['password'] == None: params['password'] = getpass.getpass('Password: ')
    values = { 'username' : params['userID'], 'password': params['password'] }
    data = urlencode(values)
    
    # Build the password manager.  Yes, this uses urllib2 rather than requests
    # This is to make the code as portable as possible for users for whom
    # requests isn't yet part of their system python, and to avoid having 
    # any dependencies if possible:
    pswd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    pswd_mgr.add_password(None, update_script_url, params['userID'], params['password'])
    handler = urllib2.HTTPBasicAuthHandler(pswd_mgr)
    opener = urllib2.build_opener(handler)
    
    # Install the opener:
    urllib2.install_opener(opener)
    try: response = opener.open(update_script_url)
    except urllib2.HTTPError, error:
        user_info.append('Problem logging into Spitzer microlensing observing portal: ' + error.reason)
	return user_info
    user_info.append('Logged into Spitzer microlensing observing portal as '+str(params['userID']))
    
    # Looping over all targets in the object_list, submit the requested update 
    # for each object's observer list:
    for object in params['object_list']:
        
	# Parse the name of the object into full-length format for disambiguity and form the event_name/
	# mode combination needed for submission:
	if len(object) < 10 and '-' not in object: full_name = swapname_public.swapname_public(short_name=object)
	else: full_name = object
	event_observer = full_name + '_' + params['observer_id']
	
	# Compose the submission to the online interface:
        form_data = { }
        if str(params['mode']).lower() == 'add': form_data['ADD_OBSERVER'] = event_observer
        if str(params['mode']).lower() == 'remove': form_data['DEL_OBSERVER'] = event_observer
        data = urlencode(form_data)
	
	# Send the request to the online system and harvest the response:
        req = urllib2.Request(update_script_url,data)
        try: response = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            user_info.append('Problem updating observer list: ' + error.reason)
            return user_info
        page_html = response.readlines()
	user_info.append(parse_response(page_html))
    
    return user_info

#################################
# PARSE RESPONSE
def parse_response(page_html):
    '''Function to extract the required information from the HTML page returned'''
    
    # Default return message:
    return_message = 'ERROR: unexpected output encountered from online interface'
    
    # Identify the relevant line in the HTML output:
    for line in page_html:
        if '<h3 style' in line and 'Observer' in line:
	    i1 = line.index('Observer')
	    i2 = line[i1:].index('<')
	    return_message = line[i1:i1+i2]
    
    return return_message

#################################
# PARSE COMMANDLINE ARGUMENTS
def parse_cl_args():
    '''Function to parse and verify the arguments given at the commandline'''
    
    # Initialize all possible options:
    params = { 'userID': None,
               'password': None,
               'observer_id': None,
	       'object_list': [],
	       'mode': None }

    # First check for help or version, since these just result in screen output:
    if '-help' in argv:
        print help_text
	exit()
    if '-version' in argv:    
        print version
	exit()
    
    # Next search for user authentication, since this requires two arguments and
    # needs to prompt for either one being missing:
    if '-user' in argv:
        i = argv.index('-user')
	try: params['userID'] = argv[i+1]
        except IndexError:
	    print 'ERROR: missing username in argument list'
	    exit()
	    
	try:
	    i = argv.index('-pass')
	    try: params['password'] = argv[i+1]
            except IndexError:
	        print 'ERROR: missing password in argument list'
	        exit()
        except ValueError:
	    print 'ERROR: missing password in argument list'
	    exit()
	 
    if '-pass' in argv:
        i = argv.index('-pass')
	try: params['password'] = argv[i+1]
        except IndexError:
	    print 'ERROR: missing password in argument list'
	    exit()
        
	try:
	    i = argv.index('-user')
	    try: params['userID'] = argv[i+1]
            except IndexError:
	        print 'ERROR: missing username in argument list'
	        exit()
        except ValueError:
	    print 'ERROR: missing username in argument list'
	    exit()   
    
    # Check for the target to be updated:
    if '-target_id' in argv:
        i = argv.index('-target_id')				  
        try:						      
             params['object_list'].append(argv[i+1])
        except IndexError:				      
            print 'ERROR: missing target name from argument list'	      
            exit()					      
    else:
    	print 'ERROR: no target given'  
    	exit()  

    # Now check for the remaining arguments:
    req_args_list = [ '-mode', '-observer_id' ]
    for argument in req_args_list:
        par_name = argument.replace('-','')
        if argument in argv:					  
            i = argv.index(argument)				  
            try:						  
        	 params[par_name] = argv[i+1]			  
            except IndexError:  				  
        	print 'ERROR: missing ' + par_name + ' value from argument list'	  
        	exit()  					  
        else:
	    print 'ERROR: missing ' + par_name + ' from argument list'	  
            exit()  
    
    return params
    
#################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    # Parse commandline arguments. 
    # This also handles the display of help and version text. 
    params = parse_cl_args()
    
    # Query the Spitzer target list and output as requested:
    user_info = update_observer_list(params)
    
    # Output info statements:
    for line in user_info: print line

