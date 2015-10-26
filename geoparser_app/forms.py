from django import forms

class DocumentForm(forms.Form):
    title = forms.CharField(max_length=50)
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )