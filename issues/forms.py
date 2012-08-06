from django import forms
from issues.models import Issue, IssueComment

class NewIssue(forms.ModelForm):
    class Meta:
        model = Issue
        
class NewComment(forms.ModelForm):
    class Meta:
        model = IssueComment
        
class ChangeLabel(forms.Form):
    label = forms.CharField(max_length=1, widget=forms.Select(choices=Issue.LABELS))
    title = forms.CharField(max_length=30)
    deadline = forms.DateField()
    
class EditIssue(forms.Form):
    content = forms.CharField(widget=forms.widgets.Textarea(attrs={'class':'input-xlarge'}))
    
class EditComment(forms.Form):
    comment = forms.CharField(widget=forms.widgets.Textarea(attrs={'class':'input-xlarge'}))