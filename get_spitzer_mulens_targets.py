#!/usr/bin/env python
###############################################################################
#     	      	      	GET SPITZER MICROLENSING TARGETS
#
# Purpose:
#    To submit and update targets for the Spizter Microlensing program to the 
#    online observing program coordination system.  
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

###############################
# DECLARED STATEMENTS
help_text = '''                     GET SPITZER MICROLENSING TARGETS

This script is designed to fetch the current list of targets for the 
Spizter Microlensing Program from the online observing program 
coordination system.  

Operation:
    From the commandline, type:
    > python get_spitzer_mulens_targets.py [options] 

Inputs (all optional): 
   -help      Displays this help text
   -version   Displays the version string
   -file [path-to-input-file] Requires a second argument giving a path to the output file to be written.
   -user [ID] -pass [code]  Requires both -user and -pass arguments to be given, followed by
              the respective access codes.  These will be prompted for if not given. 
   -targets-only  Returns only the target dictionary, no other output. 
   -history  [file-path]  Records any successful targetlist query to local disk.  This file will be
               overwritten by subsequent successful queries, but will be read back if a query fails.  

Modes:
   This program queries the online Spitzer Microlensing portal for the up-to-date target list.
   If no arguments are given, the information will be printed to screen.  
   If the -file flag is used, the same output will be written to an ASCII text file at
   the file path given.  
   If the -history flag is used, the target list output will be the online targetlist if it can be
   queried successfully.  If for some reason this is unavailable, the data in the given file will be
   returned as a fallback.  Any successful online query will cause this file to be updated.  
'''

version = 'get_spitzer_mulens_targets_v1.2'

#################################
# FUNCTION REQUEST TARGET LIST
def request_target_list(params):
    '''Function to request the up to date Spitzer microlensing target list from the online
    portal.
    
    This function requires the following parameter input dictionary:
    params = { 'userID': <given or prompted for>,
               'password': <given or prompted for>,
               'output_file': <file path, None, optional>,
               'history': <file path, None, optional>,
	       'targets-only': {True,False, Default: False} }
    
    If calling this function from another Python code, setting targets-only=True will 
    suppress all other screen or file output and return only the dictionary of targets of the
    form:
    targets = { target_name1: target_object1, 
                target_name2: target_object2, ...
	      }
    Each object is an instance of the MulensTarget class. 
    The function also returns the list user_info, which contains a list of information and/or error
    messages in the sequence they occurred.  
    '''
    
    # Initialize targets dictionary and message, returned in all cases:
    targets = {}
    user_info = []
        
    # Compose authentication details if not already available:
    if params['userID'] == None: params['userID'] = raw_input('Username: ')
    if params['password'] == None: params['password'] = getpass.getpass('Password: ')
    values = { 'username' : params['userID'], 'password': params['password'] }
    data = urlencode(values)
    
    # First attempt to harvest the targetlist from the online portal. 
    (targets, user_info, valid_targets) = fetch_online_targetlist(targets, user_info, params)
    
    # If the online query was unsuccessful, and the history option is not set, return
    # empty handed:
    if valid_targets == False and params['history'] == None:
        return targets, user_info
    
    # If the online query was unsuccessful, and the history option is set, attempt to read
    # the targetlist from local disk:
    if valid_targets == False and params['history'] != None:
        (targets, user_info, valid_targets) = read_local_target_list(targets,user_info,params)
	
    # Output the returned data according to user instructions:
    if valid_targets == True:
        if params['output_file'] == None and params['targets-only'] == False:
            for target_name,target in targets.items(): print target.summary()
        if params['output_file'] != None: output_local_target_list(targets,params['output_file'])
        if params['history'] != None: output_local_target_list(targets,params['history'])
    
    return targets, user_info

#################################
# FETCH ONLINE TARGETLIST
def fetch_online_targetlist(targets, user_info, params):
    '''Function to harvest the target list from the online portal'''
    
    # Status flag, indicates success or failure of online query:
    status = True
    
    # URL of submission page:
    url = 'http://robonet.lcogt.net/cgi-bin/private/cgiwrap/robouser/spitzer_target_list.cgi'

    # Build the password manager.  Yes, this uses urllib2 rather than requests
    # This is to make the code as portable as possible for users for whom
    # requests isn't yet part of their system python, and to avoid having 
    # any dependencies if possible:
    pswd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    pswd_mgr.add_password(None, url, params['userID'], params['password'])
    handler = urllib2.HTTPBasicAuthHandler(pswd_mgr)
    opener = urllib2.build_opener(handler)
    
    # Install the opener:
    urllib2.install_opener(opener)
    try: response = opener.open(url)
    except urllib2.HTTPError, error:
        user_info.append('Problem logging into Spitzer microlensing observing portal: ' + error.reason)
	status = False
	return targets, user_info, status
    user_info.append('Logged into Spitzer microlensing observing portal as '+str(params['userID']))
    
    # Compose the request to the target server - no parameters are required:
    url_params = { }
    data = urlencode(url_params)
	
    # Send the request to the online system and harvest the response:
    req = urllib2.Request(url,data)
    try: response = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        user_info.append('Problem fetching data from Spitzer microlensing observing portal: ' + error.reason)
	status = False
	return targets, user_info, status
    page_html = response.readlines()
    
    # Extract the ASCII target information from the returned page: 
    targets = parse_target_list_html(page_html)
    user_info.append('Source of targets: online targetlist')
    
    return targets, user_info, status
    
#################################
# OUTPUT TARGET LIST TO LOCAL FILE
def output_local_target_list(targets,file_path):
    '''Function to output the target dictionary to a file on local disk. 
    This function will overwrite any existing file at file_path.
    '''
    
    fileobj = open(file_path,'w')
    for target_name,target in targets.items(): fileobj.write(target.summary() + '\n')
    fileobj.close()
    

#################################
# READ TARGET LIST FROM LOCAL FILE
def read_local_target_list(targets,user_info,params):
    '''This function returns a target dictionary read from an input file on local disk.'''
    
    # Initialise status:
    status = True

    # Check we can find the file:
    if params['history'] == None:
        user_info.append('ERROR: No history file specified')
	status = False
	return targets, user_info, status
    if path.isfile(params['history']) == False:
         user_info.append('ERROR: Cannot find local target file '+params['history'])
	 status = False
         return targets, user_info, status
    
    # Read and parse the input file:
    fileobj = open(params['history'],'r')
    file_lines = fileobj.readlines()
    fileobj.close()
    for line in file_lines:
        if line.lstrip()[0:1] != '#':
            target = target_class.MulensTarget()
	    target.set_params(line)
	    targets[target.short_name] = target
    user_info.append('Source of targets: '+str(params['history']))
    
    return targets, user_info, status
    
#################################
# PARSE THE TARGET LIST TABLE
def parse_target_list_html(page_html):
    '''Function to extract the information from the target list HTML table. 
    Although there are number of HTML-parsing libraries out there for this purpose, this is 
    written explicitly to avoid introducing a dependency requirement for users.'''
    
    # Functions to parse specific lines in the table:
    def parse_header_line(line):
        entry = line.replace('</th><th>',' ').replace('<th>',' ').replace('</th>',' ')
	entry = entry.replace('colspan="3"','').replace('colspan="2"','').replace('align="middle"','')
        entry = entry.replace('<th >',' ').replace('<th  >',' ')
	entry = entry.replace('<sub>','_').replace('</sub>','').replace('\n','')
	if entry[0:1] == '+': entry = entry[1:]
	entry = entry.lstrip()
	return entry
    
    def parse_content_line(line):
        entry = line.replace('<tr>','').replace('</tr>','').replace('\n','')
	entry = entry.replace('<td></td>','    ')
	entry = entry.replace('</td><td>',' ').replace('<td>','').replace('<b>','').replace('</b>','')
	entry = entry.replace('</td>','').replace('&','').replace(';','_').replace('<br>',':')
	
	if '<a href' in entry:
	    i0 = line.index('<a href')
	    i1 = line.index('</a>')
	    i1 = line[i0:i1].index('>') + 1
	    entry = entry[i1:].replace('</a>',' ')
	#entry = entry.lstrip()
	
	return entry
    
    
    # Initialise target dictionary:
    targets = {}
    
    # Loop over each line of the returned HTML table.  The start and end of the target list
    # is indicated by the tags >>>>START TARGET LIST '  ' <<<<END TARGET LIST'
    table_headers = ['']
    table_entries = []
    in_table = False
    for line in page_html:
	
	# Identify the start and end of the target table (distinguishing it from the other
	# tables used in the page formatting).  At these flags, switch on and off the 
	# recording of data:
	
        if in_table == False and 'START TARGET LIST' in line:
	    in_table = True
	if in_table == True and 'END TARGET LIST' in line:
	    in_table = False
	
	# Parse table content:
	if in_table == True:
	    
	    # Distinguish between header and table entry information. 
	    # The first line of the table header is written in several sections, which
	    # need to be concatenated this way.  
	    if '<th' in line:table_headers[0] = table_headers[0] + parse_header_line(line)
	
	    # The second line of the table isn't marked as a header but contains more info
	    # on the column divisions:
	    if 'recommended' in line: table_headers.append( parse_content_line(line) )
	        
	    # Any other line containing at least one <td> is a content line, but
	    # for ASCII output we need to exclude lines containing graphics:
	    else:
	        if '<td>' in line and 'img src' not in line and 'form' not in line: 
		    entry = parse_content_line(line)
		    if len(entry.replace(' ','').replace('\t','')) > 0: 
		        target = target_class.MulensTarget()
		        target.set_params(entry)
		        targets[target.short_name] = target
			
    # Compile the table data:
    # Note this is now no longer returned; code may be removed anon. depending on how useage 
    # develops. 
    table_data = ''
    for hdr in table_headers: table_data = table_data + '# ' + hdr + '\n'
    for entry in table_entries:  table_data = table_data + entry + '\n'
    
    return targets

#################################
# PARSE COMMANDLINE ARGUMENTS
def parse_cl_args():
    '''Function to parse and verify the arguments given at the commandline'''
    
    # Initialize all possible options:
    params = { 'userID': None,
               'password': None,
               'output_file': None,
	       'targets-only': False,
	       'history': None }

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

    # Now check for an output file name:
    if '-file' in argv:
        i = argv.index('-file')
	try:
	     params['output_file'] = argv[i+1]
        except IndexError:
	    print 'ERROR: missing output filename in argument list'
	    exit() 
    
    # Now check for an output file name:
    if '-history' in argv:
        i = argv.index('-history')
	try:
	     params['history'] = argv[i+1]
        except IndexError:
	    print 'ERROR: missing target list history filename in argument list'
	    exit() 
	    
    # ...and check for no output option (returns target dictionary only):
    if '-targets-only' in argv: params['targets-only'] = True
    
    
    return params
    
#################################
# COMMANDLINE RUN SECTION
if __name__ == '__main__':
    
    # Parse commandline arguments. 
    # This also handles the display of help and version text. 
    params = parse_cl_args()
    
    # Query the Spitzer target list and output as requested:
    (target_dict, user_info) = request_target_list(params)
    
    # Output info statements:
    for line in user_info: print line
