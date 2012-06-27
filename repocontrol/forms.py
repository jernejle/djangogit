from django import forms
from repocontrol.models import Repository, CommitComment
from django.core.exceptions import ObjectDoesNotExist

class NewRepo(forms.ModelForm):
    class Meta:
        model = Repository
        
    def clean(self):
        cleaned_data = super(NewRepo,self).clean()
        new = cleaned_data.get('name')
        
        try:
            repo = Repository.objects.get(name=new)
        except ObjectDoesNotExist:
            repo = None
        
        if repo:
            raise forms.ValidationError("Repository with the same name already exists")
        return cleaned_data


class NewComment(forms.ModelForm):
    class Meta:
        model = CommitComment