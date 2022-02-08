from random import choice
from difflib import get_close_matches
from markdown2 import Markdown
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from . import util
from .forms import EntryForm, SearchForm

def index(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['q']
            '''
            create a list of 'entries'
            create a dict where key is the entries.lower() & value is entries
            'exact_match_found' returns a list
            thus 'exact_match_found[0]' is passed in kwargs as a string
            '''
            search_list = util.list_entries()
            search_dict = {key.lower():key for key in search_list}
            exact_match_found = get_close_matches(search_term.lower(), list(search_dict.keys()), n=1, cutoff=1)
            if exact_match_found:
                exact_match = exact_match_found[0]
                return HttpResponseRedirect(reverse('encyclopedia:entry_page', kwargs={'entry_name': search_dict.get(exact_match) }))
            else:
                search_results = get_close_matches(search_term.lower(), list(search_dict.keys()), n=10 , cutoff=0.4)
                return render(request, "encyclopedia/index.html", {
                    "entries": [search_dict.get(key) for key in search_results]
                    })
        else:
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries()
                })
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })

def entry_page(request, entry_name):
    if entry_name not in util.list_entries():
        return render(request, "encyclopedia/index.html", {
                "entries": None
                })
    else:
        markdowner = Markdown()
        return render(request, "encyclopedia/entry_page.html", {
            "entry_name": entry_name, "content": markdowner.convert(util.get_entry(entry_name))
        })

def create_entry(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            if not util.get_entry(title):
                content = form.cleaned_data['content'].encode("utf-8")
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('encyclopedia:entry_page', kwargs={'entry_name': title}))
            else:
                return HttpResponseRedirect(reverse('encyclopedia:edit_entry', kwargs={'entry_name': title}))
        else:
            return render(request, "encyclopedia/create_entry.html", {
                'form': form
            })
    else:
        return render(request, "encyclopedia/create_entry.html", {
            'form': EntryForm()
        })

def edit_entry(request, entry_name):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content'].encode("utf-8")
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('encyclopedia:entry_page', kwargs={'entry_name': title}))
        else:
            return render(request, "encyclopedia/edit_entry.html", {
            'entry_name': entry_name, 'form': form
        })
    else:
        content = util.get_entry(entry_name)
        return render(request, "encyclopedia/edit_entry.html", {
            'entry_name': entry_name, 'form': EntryForm(initial={'title':entry_name, 'content':content})
        })

def random_entry(request):
    '''
    'choice' function returns a random sequence from a list of sequence
    '''
    title = choice(util.list_entries())
    return HttpResponseRedirect(reverse('encyclopedia:entry_page', kwargs={'entry_name': title}))