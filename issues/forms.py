from django import forms
from issues.models import Issue, IssueComment

class NewIssue(forms.ModelForm):
    class Meta:
        model = Issue
        
class NewComment(forms.ModelForm):
    class Meta:
        model = IssueComment