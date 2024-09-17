import pandas as pd
import json
from django.shortcuts import render
from django.http import JsonResponse
from .data_analysis import perform_data_analysis
from .models import DynamicTableLoader
from .dash_app import get_dash_data 


def data_analysis_view(request):
    years = request.GET.getlist('years')
    arrondissements = request.GET.getlist('arrondissements')

    # Fetch data directly using get_dash_data
    df = get_dash_data(years=years, arrondissements=arrondissements)

    print(years)
    print(arrondissements)
    print(df)

    if df.empty:
        return render(request, 'index.html', {
            'summary_stats_array': json.dumps([]),  # Pass empty data
        })

    # Convert DataFrame to a list of lists and column names for the frontend
    summary_stats_array = df.fillna('').values.tolist()  
    context = {
        'summary_stats_array': json.dumps(summary_stats_array), 
    }

    return render(request, 'index.html', context)


def load_data_view(request):
    years = request.GET.getlist('years')
    arrondissements = request.GET.getlist('arrondissements')

    print('Received Years:', years)
    print('Received Arrondissements:', arrondissements)

    if not years or not arrondissements:
        return JsonResponse({'error': 'Years or arrondissements not provided'}, status=400)

    # Fetch data directly using get_dash_data
    df = get_dash_data(years=years, arrondissements=arrondissements)

    print(df)

    if df.empty:
        return JsonResponse({'data': [], 'columns': []})

    data = df.fillna('').values.tolist()
    columns = [{'title': col} for col in df.columns]

    return JsonResponse({'data': data, 'columns': columns})


def fetch_column_data(request):
    column_name = request.GET.get('column', None)
    years = request.GET.getlist('years[]', None)
    arrondissements = request.GET.getlist('arrondissements[]', None)

    # Fetch data directly using get_dash_data
    data = get_dash_data(years=years, arrondissements=arrondissements)

    print(years)
    print(arrondissements)
    print(data)

    # Ensure column exists
    if column_name and column_name in data.columns:
        response_data = data[[column_name]].to_dict(orient='records')
        return JsonResponse(response_data, safe=False)

    return JsonResponse({"error": "Invalid request or column not found"}, status=400)
