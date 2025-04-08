from django import forms
from .models import Submission, Discussion

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']