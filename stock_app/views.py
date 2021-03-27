from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StockForm
import json
import requests
import plotly.express as px
import os
from bs4 import BeautifulSoup
from .models import Stock
# Create your views here.


ticker_get = requests.get('https://stockanalysis.com/stocks/')
soup = BeautifulSoup(ticker_get.content, 'html.parser')
tick_list = []
for link in soup.find_all('a'):
    tick_split = link.text.split('-')
    tick_list.append(tick_split[0].strip())
    tick_list_clean = tick_list[16:-26]


def home(request):
    if request.method == 'POST':
        ticker = request.POST['ticker_name']
        pk = 'pk_49ff2caccff94132a476683575424aeb'
        api_request = requests.get(f'https://cloud.iexapis.com/stable/stock/{ticker}/quote?token={pk}')

        try:
            api = json.loads(api_request.content)
            api_clean = [api['week52Low'], api['iexRealtimePrice'], api['week52High']]
            api_clean_titles = ['52Wk Low', 'Price', '52Wk High']
            print(api_clean)
            fig = px.bar(x=api_clean_titles, y=api_clean, labels= {'x': 'Metrics', 'y': 'USD'})
            os.chdir(
                '/Users/emiledurham/Desktop/Udemy/elder_udemy/elder_django_udemy3/stock_project/stock_app/templates')
            graph = fig.to_html(full_html=False, default_height=500, default_width=700)
            return render(request, 'home.html', {'api': api, 'graph': graph, 'tick_list_clean': tick_list_clean})

        except Exception as e:
            api = "Error..."
        return render(request, 'home.html',{'api': api, 'tick_list_clean': tick_list_clean})
    return render(request, 'home.html', {'tick_list_clean': tick_list_clean})


def about(request):
    return render(request, 'about.html', {'tick_list_clean': tick_list_clean})


def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock Has Been Added')
            return redirect('add_stock')
    else:
        ticker_db = Stock.objects.all()
        tick_output = []
        for tick in ticker_db:
            pk = 'pk_49ff2caccff94132a476683575424aeb'
            api_request = requests.get(f'https://cloud.iexapis.com/stable/stock/{tick}/quote?token={pk}')
            try:
                api = json.loads(api_request.content)
                tick_output.append(api)
                print(tick_output)
            except Exception as e:
                api = 'Error...'

        return render(request, 'add_stock.html', {'tick_list_clean': tick_list_clean, 'ticker_db': ticker_db,'tick_output': tick_output})
    return render(request, 'add_stock.html', {'tick_list_clean': tick_list_clean})


def delete(request, stock_id):
    item = Stock.objects.get(pk=stock_id)
    item.delete()
    messages.success(request, 'Stock Has Been Deleted!')
    return redirect('delete_stock')


def delete_stock(request):
    ticker_db = Stock.objects.all()
    return render(request, 'delete_stock.html', {'ticker_db': ticker_db})
