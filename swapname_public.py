##########################################
# SWAPNAME_PUBLIC
def swapname_public(full_name=None, short_name=None, len_event_number=4):
    '''Function to swap between short- and long-hand naming conventions for microlensing events, 
    applying the survey-code abbreviation outlined by A. Gould (as opposed to the convention
    used internally by RoboNet software):
    O = OGLE
    M = MOA
    K = KMTNet
    Kwargs are:
        full_name  if given, name returned will be in short-hand format
	short_name if given, name returned will be in long-hand format
	len_event_number  is 4 by default but can be set to another integer
    This function assumes all dates are later than 2000.  
    '''
    
    #print 'Got full_name=' + repr(full_name) + ' short_name=' + repr(short_name)
    
    # Catch case where input is improperly constructed:
    if full_name == None and short_name == None: return None
    
    # Initialise name components:
    prefix = None
    year = None
    event_number = None
    converted_name = None
    
    # Convert fullname to short-hand convention:
    if full_name != None:
        surveys = { 'OGLE': 'O', 'MOA': 'M', 'KMT': 'K' }
        for key in surveys.keys():
	    if key in full_name: prefix = surveys[key]
	year = full_name.split('-')[1][2:4]
	event_number = full_name.split('-')[-1]
        
	converted_name = prefix + 'B' + year + event_number
	
    # Convert short-hand format to full:
    elif short_name != None:
        surveys = { 'O': 'OGLE', 'M': 'MOA', 'K': 'KMT' }
        for key in surveys.keys():
	    if key == short_name[0:1]: prefix = surveys[key]
        year = '20' + short_name[2:4]
        event_number = short_name[-(len_event_number):]
	converted_name = prefix + '-' + year + '-BLG-' + event_number
	
    return converted_name
