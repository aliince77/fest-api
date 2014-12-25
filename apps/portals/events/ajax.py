# For simple dajax(ice) functionalities
from django.utils import simplejson
import json
from pytz import timezone
import unicodedata
from dajaxice.decorators import dajaxice_register

# For rendering templates
from django.template import RequestContext
from django.template.loader import render_to_string

# Decorators
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings 

#models
from django.contrib.auth.models import User
from apps.users.models import ERPProfile, UserProfile, Dept, Subdept, Team
from apps.events.models import EventTab, Event, EventSchedule

from apps.portals.events.forms import AddSlotForm

#dajaxice stuff
from dajaxice.utils import deserialize_form

import re

@dajaxice_register
def hello(request):
    return json.dumps({'message': 'aslkfhas'})


@dajaxice_register
def show_tabs(request,event_name,username):
    event_object=Event.objects.get(name=event_name)
    user_object=User.objects.get(username=username)
    has_perm = permission(event_object,user_object)
    tabs_object_list=event_object.eventtab_set.all()
#tabs_names_list is a string with a set of event-tab-names -separated by commas
    tabs_names_list=''
    for i in tabs_object_list:
	tabs_names_list=tabs_names_list+i.name+','
    return json.dumps({'tabs_names_list':'%s' % tabs_names_list,'event_name':event_name,'has_perm':has_perm})


@dajaxice_register
def show_tabs_description(request,event_name,event_tab,has_perm):
    event_object=Event.objects.get(name=event_name)
    event_tab=EventTab.objects.get(name=event_tab,event=event_object)
    description=event_tab.content
    description=" ".join(description.split())
    #print description
    return json.dumps({'description': description,'event_name':event_name,'event_tab_name': event_tab.name,'has_perm':has_perm})

#"<br/>".join(description.split("\r"))
#ARUN - CHANGES MADE HERE
#Function for setting permissions to edit Event Tabs 
def permission(event_object,user_object):
        return "yes"
	events_dept=Dept.objects.get(name='events')
	qms_dept=Dept.objects.get(name='qms')
	if hasattr(user_object,'erp_profile'):
		a=5
	else:
		if event_object.has_tdp:
			return "participant_event_has_tdp"
		else:
			return "participant"
	if user_object.is_staff or user_object.erp_profile in event_object.coords.all():
		return "yes"
	else:
		return "no"




@dajaxice_register
def register(request,event_name,username):
    user_object=User.objects.get(username=username)
    userprofile_object=UserProfile.objects.get(user=user_object)
    event_object=Event.objects.get(name=event_name)
    event_object.participants_registered.add(userprofile_object)
    event_object.save()
    return json.dumps({'message':event_name+username})


@dajaxice_register
def delete_tab(request,event_name,event_tab_name,username):
    event_object=Event.objects.get(name=event_name)
    event_tab=EventTab.objects.get(name=event_tab_name,event=event_object)
    event_tab.delete()
    return json.dumps({'message':'The event-tab '+event_tab_name+' from the event '+event_name+' has been deleted','username':username,'event_name':event_object.name})





@dajaxice_register
def add_tab(request,username,add_tab_form):
    add_tab_form=deserialize_form(add_tab_form)
    message=""    
    if add_tab_form['tab_name']!='' and  add_tab_form['tab_name'][0]!=' ':
		event_tab=EventTab()
		event_tab.name=add_tab_form['tab_name']
		event_tab.content=add_tab_form['tab_description']
		event_tab.event=Event.objects.get(name=add_tab_form['event_name'])
		event_tab.save()
		message="The " + add_tab_form['tab_name'] + " tab has been successfully added to the " + add_tab_form['event_name'] + " event"
    return json.dumps({'message': message,'username':username,'event_name':add_tab_form['event_name']})



@dajaxice_register
def edit_tab(request,username,edit_tab_form):
    edit_tab_form=deserialize_form(edit_tab_form)
    message=""
    if edit_tab_form['tab_Name']!='' and  edit_tab_form['tab_Name'][0]!=' ':
			event_object=Event.objects.get(name=edit_tab_form['event_Name_edit_form'])
			event_tab=EventTab.objects.get(name=edit_tab_form['event_tab_Name_edit_form'],event=event_object)

			event_tab.name=edit_tab_form['tab_Name']
			event_tab.content=edit_tab_form['tab_Description']
			event_tab.event=Event.objects.get(name=edit_tab_form['event_Name_edit_form'])
			event_tab.save()

			message="The " + edit_tab_form['tab_Name'] + " tab from the event " + edit_tab_form['event_Name_edit_form'] + "  has been successfully Edited."

    return json.dumps({'message': message,'username':username,'event_name':event_object.name})
    
    
from apps.portals.events.forms import AddEventForm    

@dajaxice_register
def edit_event_details(request,event_name):
	event_object=Event.objects.get(name=event_name)
	form = AddEventForm(instance=event_object).as_table()
	event_id = event_object.id
	try:
		image_source= str(event_object.event_image.url)
	except Exception,e:
		image_source=""
	
	slot_id=""
	slot_start=""
	slot_end=""
	slot_comment=""
	slot_venue=""

	try:
		event_slots= EventSchedule.objects.filter(event=event_object)
		for slot in event_slots:
			slot_id=slot_id+str(slot.id)+"|"
			slot_start=slot_start+((slot.slot_start).astimezone(timezone(settings.TIME_ZONE)).strftime('%c'))+"|"
			slot_end=slot_end+((slot.slot_end).astimezone(timezone(settings.TIME_ZONE)).strftime('%c'))+"|"
			slot_comment=slot_comment+ str(slot.comment) + "|" 
			slot_venue=slot_venue + str(slot.venue) + "|"
		length= len(event_slots)
	except Exception,e:
		pass
	return json.dumps({'form':form, 'message': 'message','event_name':event_name,'event_id':event_id,'image_source':image_source, 'slot_venue':slot_venue, 'slot_comment':slot_comment, 'slot_start':slot_start,'slot_end':slot_end, 'length_count':length, 'slot_id':slot_id})
    
    
@dajaxice_register
def display_add_event(request):
	form = AddEventForm().as_table()
	return json.dumps({'form':form})

#try to make the deserialized form of the type addeventform then validate it

@dajaxice_register    
def add_event(request,event_form):
	message="Your form has the following errors <br>"
	event_form = AddEventForm(deserialize_form(event_form))
	if event_form.is_valid():
		event_form.save()
		message="successfully added event"
	else:
		for field in event_form:
			for error in field.errors:
				message=message+field.html_name+" : "+error+"<br>"
				
	return json.dumps({'message': message})
	

from django.core.exceptions import ValidationError
@dajaxice_register    
def edit_event(request,event_name,edit_event_form):
	message="Your form has the following errors <br>"
	event_object=Event.objects.get(name=event_name)
	edit_event_form = AddEventForm(deserialize_form(edit_event_form), instance=event_object)
	if edit_event_form.is_valid():
		#event_object.name=edit_event_form.cleaned_data['name']
		#event_object.short_description=edit_event_form.cleaned_data['short_description']
		#event_object.event_type=edit_event_form.cleaned_data['event_type']
		#event_object.category =edit_event_form.cleaned_data['category']
		#event_object.has_tdp=edit_event_form.cleaned_data['has_tdp']
		#event_object.team_size_min=edit_event_form.cleaned_data['team_size_min']
		#event_object.team_size_max=edit_event_form.cleaned_data['team_size_max']
		#event_object.registration_starts=edit_event_form.cleaned_data['registration_starts']
		#event_object.google_group=edit_event_form.cleaned_data['google_group']
		#event_object.email=edit_event_form.cleaned_data['email']
		#event_object.coords=edit_event_form.cleaned_data['coords']
		#event_object.save()	
                edit_event_form.save()
		temp=1
		message="successfully added event"
	else:
		temp=0
		for field in edit_event_form:
			for error in field.errors:
				message=message+field.html_name+" : "+error+"<br>"


	return json.dumps({'message': message,'temp':temp})
	
	
	
	
	
@dajaxice_register    
def view_edit_event(request):
	event_names=""
	event_emails=""
	event_categories=""
	event_array=Event.objects.all()
	for event in event_array:
		event_names=event_names+event.name+"|"
		event_emails=event_emails+event.email+"|"
		event_categories=event_categories+event.category+"|"
	return json.dumps({'event_names': event_names,'event_emails':event_emails,'event_categories':event_categories})
	


@dajaxice_register    
def delete_event(request,event_name):
	event_object=Event.objects.get(name=event_name)
	event_object.delete()
	message="The event " + event_name + " has been successfully deleted."
	return json.dumps({'message':message})
	
	
	
@dajaxice_register    
def reg_list(request,event_name):
	event_object=Event.objects.get(name=event_name)
	event_registrations=event_object.event_registered.all()
	user_names=""
	team_names=""
	info=""
	for reg in event_registrations:
		user_names=user_names + reg.users_registered.username +" |"
		if reg.teams_registered==None:
			team_names=team_names + "None |"
		else:
			team_names=team_names + reg.teams_registered.name +" |"
		info=str(info) + str(reg.info) + " |"
	return json.dumps({'event_name':event_name,'user_names':user_names,'team_names':team_names,'info':info})

@dajaxice_register    
def participant_info(request,participant_name,team_name):

	try :
		data=[]
		temp={}		
		team = Team.objects.get(name=team_name)
		members=team.members.all()
		for i in range(len(members)):
			temp={}
			temp['name']=str(members[i].username)
			temp['number']=members[i].profile.mobile_number
			temp['email']=str(members[i].email)
			data.append(temp)
	except Exception, e:
		temp={}
		data=[]
		participant = User.objects.get(username=participant_name)
		temp['name']=str(participant_name)
		temp['number']=participant.profile.mobile_number
		temp['email']=str(participant.email)
		data.append(temp)
	return json.dumps({'inf':data,'len':len(data),})	


@dajaxice_register
def display_add_event_slot(request):
	form = AddSlotForm().as_table()
	slot_event=""
	slot_start=""
	slot_end=""
	slot_comment=""
	slot_venue=""
	slot_array = EventSchedule.objects.all()
	for slot in slot_array:
		slot_event=slot_event+slot.event.name+"|"
		slot_start=slot_start+((slot.slot_start).astimezone(timezone(settings.TIME_ZONE)).strftime('%c'))+"|"
		slot_end=slot_end+((slot.slot_end).astimezone(timezone(settings.TIME_ZONE)).strftime('%c'))+"|"
		slot_comment=slot_comment+ str(slot.comment) + "|" 
		slot_venue=slot_venue + str(slot.venue) + "|"
	return json.dumps({'form':form, 'slot_venue':slot_venue, 'slot_comment':slot_comment, 'slot_event': slot_event,'slot_start':slot_start,'slot_end':slot_end})

@dajaxice_register    
def add_slot(request,slot_form):
	message="Your form has the following errors <br>"
	slot_form = AddSlotForm(deserialize_form(slot_form))
	if slot_form.is_valid():
		slot_form.save()
		message="successfully added event"
	else:
		for field in slot_form:
			for error in field.errors:
				message=message+field.html_name+" : "+error+"<br>"

	return json.dumps({'message': message})		

@dajaxice_register    
def delete_slot(request,slot_id):
	message="successfully Deleted slot"
	try:
		slot=EventSchedule.objects.get(id=int(slot_id))
		slot.delete()
	except Exception, e:
		message="no such slot exists"
	return json.dumps({'message': message})










#QMS PORTAL FUNCTIONS - IT IS HERE BECAUSE I CAN'T GET DAJAXICE FUNCTIONS TO WORK THERE. WILL SHIFT EVERYTHING THERE LATER         
from apps.users.forms import LoginForm,UserForm
from apps.users.models import Team
from apps.portals.qms.forms import AddTeamForm,UserProfileForm,AddEventRegistrationForm

from apps.events.models import EventRegistration


@dajaxice_register    
def add_user(request,userform,userprofileform):
	message="Your form has the following errors:\n"
	user_form = UserForm(deserialize_form(userform))
	user_profile_form = UserProfileForm(deserialize_form(userprofileform))
	valid=0
	
	if (user_form.is_valid() and user_profile_form.is_valid()):
		valid=1
		user = user_form.save()
		user.username=user.email
		user.password=user.email
		user.set_password(user.email)
		user.save()
		
		profile = user_profile_form.save(commit=False)
		profile.user = user
		profile.email=user.email
		if profile.mobile_number:
			profile.mobile=profile.mobile_number
		if user.first_name:
			profile.name=user.first_name
			if user.last_name:
				profile.name=user.first_name + " " + user.last_name
		profile.save()
		message="Successfully added User"
	if valid==0:
		for field in user_form:
			for error in field.errors:
				message=message+field.html_name+" : "+error+"\n"
		for field in user_profile_form:
			for error in field.errors:
				message=message+field.html_name+" : "+error+"\n"
	return json.dumps({'message': message})   
	
	
	
@dajaxice_register    
def add_team(request,teamform):
	message="Your form has the following errors:\n"
	team_form = AddTeamForm(deserialize_form(teamform))
	if team_form.is_valid():
		team_form.save()
		message="Successfully added Team"
	else:
		for field in team_form:
			for error in field.errors:
				message=message+field.html_name+" : "+error+"\n"
	return json.dumps({'message': message}) 
	
	
	
	
@dajaxice_register    
def register_user_team(request,registerform):
	message="Your form has the following errors:\n"
	register_form = AddEventRegistrationForm(deserialize_form(registerform))
	if register_form.is_valid():
		register_form.save()
		message="Successfully added registration"
	else:
		for field in register_form:
			for error in field.errors:
				message=message+field.html_name+" : "+error+"\n"
	return json.dumps({'message': message}) 	

