from django.shortcuts import render, get_object_or_404, redirect
from .models import Search, Document
from bs4 import BeautifulSoup
import requests
import re


# Create your views here.
def find_documents():
    tut_by_page = requests.get('https://www.tut.by')
    assert tut_by_page.status_code == 200
    soup = BeautifulSoup(tut_by_page.text, 'html.parser')
    for href_tag in soup.find_all(class_=re.compile('io-block-link')):
        href = href_tag.get('href')
        page = requests.get(href)
        if page.status_code == 200:
            doc_soup = BeautifulSoup(page.text, 'html.parser')
            try:
                title = doc_soup.find(itemprop='headline').text
                article_body = doc_soup.find(itemprop='articleBody')
                text = ''
                for p in article_body.find_all('p'):
                    text += p.text
                snippet = ''
                for sent in text.split('.'):
                    if len(snippet + sent + '.') <= 300:
                        snippet += sent + '.'
                Document.objects.update_or_create(title=title, defaults={'text': text, 'snippet': snippet})
            except AttributeError:
                continue


def results(request, search_id):
    search = get_object_or_404(Search, pk=search_id)
    return render(request, 'search_app/results_page.html', {'query': search.query, 'result': search.get_result()})


def index(request):
    if request.method == 'GET':
        return render(request, 'search_app/search_page.html')
    if request.method == 'POST':
        find_documents()
        query = request.POST['query']
        search, _ = Search.objects.get_or_create(query=query)
        return redirect('result', search_id=search.id)


def help_page(request):
    return render(request, 'search_app/help.html')
