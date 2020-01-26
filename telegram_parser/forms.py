from django import forms

class ConfigForm(forms.Form):
    greeting = forms.CharField(widget=forms.Textarea)
    cooldown = forms.CharField(widget=forms.Textarea)
    search = forms.CharField(widget=forms.Textarea)
    error = forms.CharField(widget=forms.Textarea)
    misunderstanding = forms.CharField(widget=forms.Textarea)
    token = forms.CharField(label='Bot Token')
    provider_token = forms.CharField(label='Payment provider token')