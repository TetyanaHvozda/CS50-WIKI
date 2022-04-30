import random

import markdown2

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.urls import reverse

from . import util
from markdown2 import Markdown

markdowner = Markdown()


class Post(forms.Form):
    title = forms.CharField(label= "Title")
    textarea = forms.CharField(widget=forms.Textarea(), label='')

class Search(forms.Form):
    item = forms.CharField(widget=forms.TextInput(attrs={'class' : 'myfieldclass', 'placeholder': 'Search'}))

class Edit(forms.Form):
    textarea = forms.CharField(widget=forms.Textarea(), label='')

def index(request):
    entries = util.list_entries()
    searched = []
    if request.method == "POST":
        form = Search(request.POST)
        if form.is_valid():
            item = form.cleaned_data["item"]
            for i in entries:
                if item in entries:
                    page = util.get_entry(item)
                    page_converted = markdowner.convert(page)
                    context = {
                        'page': page_converted,
                        'entryTitle': item,
                        'form': Search()
                    }
                    return render(request, "encyclopedia/entry.html", context)
                if item.lower() in i.lower():
                    searched.append(i)
                    context = {
                        'searched': searched,
                        'form': Search()
                    }
            return render(request, "encyclopedia/search.html", context)
        else:
            return render(request, "encyclopedia/index.html", {"form": form})
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(), "form":Search()
        })

def entry(request, title):
    markdowner = Markdown()
    entryPage = util.get_entry(title)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": title
        })
    else:
        return render(request, "encyclopedia/entry.html", {
        "page": markdowner.convert(entryPage),
        "entryTitle": title
        })



def create(request):
    if request.method == 'POST':
        form = Post(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            textarea = form.cleaned_data["textarea"]
            entries = util.list_entries()
            if title in entries:
                return render(request, "encyclopedia/error.html", {"form": Search(), "message": "Page already exist"})
            else:
                util.save_entry(title,textarea)
                page = util.get_entry(title)
                page_converted = markdowner.convert(page)

                context = {
                    'form': Search(),
                    'page': page_converted,
                    'entryTitle': title
                }

                return render(request, "encyclopedia/entry.html", context)
    else:
        return render(request, "encyclopedia/create.html", {"form": Search(), "post": Post()})

def edit(request, title):
    if request.method == 'GET':
        page = util.get_entry(title)

        context = {
            'form': Search(),
            'edit': Edit(initial={'textarea': page}),
            'title': title
        }

        return render(request, "encyclopedia/edit.html", context)
    else:
        form = Edit(request.POST)
        if form.is_valid():
            textarea = form.cleaned_data["textarea"]
            util.save_entry(title,textarea)
            page = util.get_entry(title)
            page_converted = markdowner.convert(page)

            context = {
                'form': Search(),
                'page': page_converted,
                'title': title
            }

            return render(request, "encyclopedia/entry.html", context)

def randomPage(request):
    if request.method == 'GET':
        entries = util.list_entries()
        num = random.randint(0, len(entries) - 1)
        page_random = entries[num]
        page = util.get_entry(page_random)
        page_converted = markdowner.convert(page)

        context = {
            'form': Search(),
            'page': page_converted,
            'entryTitle': page_random
        }

        return render(request, "encyclopedia/entry.html", context)
