from tkinter import Widget
from tkinter.tix import Form
from django import forms

class SearchForm(forms.Form):
    q = forms.CharField()

class EntryForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)