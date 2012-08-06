from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.contrib.auth.models import User
from userprofile.models import Message

@dajaxice_register
def read_message(request,messageid):
    if request.user.is_authenticated():
        try:
            messageid = int(messageid)
        except:
            return
    dajax = Dajax()
    message = Message.objects.get(pk=messageid,user=request.user)
    if message and not message.read:
        message.read = True
        message.save()
    return dajax.json()

@dajaxice_register
def del_message(request,messageid):
    if request.user.is_authenticated():
        try:
            messageid = int(messageid)
        except:
            return
    dajax = Dajax()
    message = Message.objects.get(pk=messageid,user=request.user)
    if message:
        message.delete()
    return dajax.json()

@dajaxice_register
def checkmessages(request):
    if not request.user.is_authenticated():
        return
    
    dajax = Dajax()
    unread = Message.objects.filter(user=request.user,read=False).count()
    dajax.assign("#messcount", "innerHTML", unread)
    return dajax.json()