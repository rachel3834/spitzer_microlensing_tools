###################################################################################
#     	      	      	    SPITZER MICROLENSING TARGET CLASS
#
# Definition of a Class of object describing a target in the Spitzer Microlensing Program
# Author:
#    Rachel Street @ LCOGT
###################################################################################

########################
# IMPORTED MODULES
import swapname_public


class MulensTarget:
    '''Class definition of a microlensing target selected for ground- and space-based simultaneous 
    observation with Spitzer'''
    
    # Initialize:
    def __init__(self):
        '''Method to describe the initialization of a target in the Spitzer Microlensing Program'''
	
	self.name = None
	self.short_name = None
        self.ra = None
        self.dec = None
	self.A0_survey = None
        self.t0_survey = None
	self.u0_survey = None
	self.tE_survey = None
	self.mag_last = None
	self.delta_t_last = None
        self.mag_model = None
        self.cadence_hrs = None
        self.spitzer_priority = None
        self.ground_priority = None
        self.observers_list = None
	self.survey_cadence = None

        self.key_list = [ 'short_name', 'ra', 'dec', 'A0_survey', 't0_survey', 'tE_survey', 'mag_last', \
	             'delta_t_last', 'mag_model', 'cadence_hrs', 'spitzer_priority', 'ground_priority', \
		     'survey_cadence', 'observers_list' ]
        self.float_keys = [ 'A0_survey', 'tE_survey', 'mag_last', 'delta_t_last', 'mag_model', 'cadence_hrs' ]
	

    # Set input parameters from table entry string:
    def set_params(self,entry):
        '''Method to set the parameters of this instance of the MulensTarget class from an
	entry in the target list table.  The entry is given as a single string.
	Format should be:
	Name RA Dec A_0 t_0 t_E  Latest_mag Delta_t Model_mag Cadence[hrs] Spizter_priority Ground_priority Survey_visits Observers_list
	
	Where the Observers list is colon-separated.
	'''
	
	# Catch any content-free input strings:
	entry_list = entry.split()
	if len(entry_list) > 0:
	    
            for i,key in enumerate(self.key_list):
	    	if key in self.float_keys: 
		    if 'none' in str(entry_list[i]).lower(): setattr(self,key,0.0)
		    else: setattr(self,key,float(entry_list[i]))
	    	else: setattr(self,key,entry_list[i])
	    	if key == 'short_name': self.name = swapname_public.swapname_public(short_name=self.short_name)

    # Return summary string:
    def summary(self):
        '''Method to print a text summary of all parameters'''
	
	summary = ''
	for key in self.key_list: summary = summary + ' ' + str(getattr(self,key))
        return summary
	
