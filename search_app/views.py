from django.shortcuts import render, get_object_or_404, redirect
from .models import Search


# Create your views here.

def results(request, search_id):
    search = get_object_or_404(Search, pk=search_id)
    return render(request, 'search_app/results_page.html', {'query': search.query, 'result': search.get_result()})


def index(request):
    if request.method == 'GET':
        return render(request, 'search_app/search_page.html')
    if request.method == 'POST':
        query = request.POST['query']
        search, _ = Search.objects.get_or_create(query=query)
        return redirect('result', search_id=search.id)


def help_page(request):
    return render(request, 'search_app/help.html')
