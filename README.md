# spitzer_microlensing_tools
Tools to interact with the Spitzer Microlensing program portal

This repository provides a toolkit for users interacting with the Spitzer Microlensing Program 
online portal. 

* Getting Help

All tools can be called from the commandline with a -help flag to display a description of the 
code and instructions on how to run it. 

* Calling get_spitzer_mulens_targets from within Python

get_spitzer_mulens_targets can be imported into your own Python module, 
and its main function, request_target_list, can be called with a simple
parameter dictionary.  For details, import the function into iPython and type
request_target_list?
The function returns a dictionary of objects of the MulensTarget class and a list of strings (user_info) which records the progress of the program and any error output.  

* -history

This code will always attempt to query the online target list for the most up to date information.  
If the history flag is set with a localdisk file path given, the code will maintain an updated local copy of the targetlist.  
If for some reason a query is unsuccessful, and the history flag is set, the code will use the history file as a fallback, re-reading the targetlist from an earlier query.  

