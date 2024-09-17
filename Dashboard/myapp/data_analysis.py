import pandas as pd
from .models import DynamicTableLoader
from django.core.cache import cache
import logging
import hashlib

def binary_search(df, column, value, start=True):
    """Perform a binary search to find the starting or ending index of a value in a sorted dataframe column."""
    low, high = 0, len(df) - 1
    result = -1
    while low <= high:
        mid = (low + high) // 2
        if df.iloc[mid][column] == value:
            result = mid
            if start:
                high = mid - 1  # Continue to search in the left half
            else:
                low = mid + 1   # Continue to search in the right half
        elif df.iloc[mid][column] < value:
            low = mid + 1
        else:
            high = mid - 1
    return result

logger = logging.getLogger(__name__)

def generate_safe_cache_key(*args):
    """Generate a safe cache key using a hash function."""
    key = ":".join(str(arg) for arg in args)
    return hashlib.md5(key.encode()).hexdigest()

def perform_data_analysis(ramses_id=None, quote_name=None, start_date=None, end_date=None, years=None, arrondissements=None, limit=10000, initial_columns_only=False):
    # Generate cache key based on parameters
    cache_key = generate_safe_cache_key('data_analysis', ramses_id, quote_name, start_date, end_date, years, arrondissements, limit, initial_columns_only)
    cached_result = cache.get(cache_key)

    if cached_result is not None:
        return cached_result

    # Load data dynamically from the partitioned tables
    data = []
    columns = []
    
    if years and arrondissements:
        for year in years:
            for arrondissement in arrondissements:
                cols, rows = DynamicTableLoader.load_data(year, arrondissement)
                if not columns:
                    columns = cols
                data.extend(rows)
    
    df = pd.DataFrame(data, columns=columns)
    
    # Apply filters
    if ramses_id:
        df = df[df['Ramses_id'] == ramses_id]
    if start_date:
        df = df[df['Date_control'] >= start_date]
    if end_date:
        df = df[df['Date_control'] <= end_date]
    if quote_name:
        df = df[df['Quote_name'] == quote_name]

    # Check if DataFrame is empty
    if df.empty:
        logger.warning("The DataFrame is empty after applying filters.")
        return pd.DataFrame()  # Return an empty DataFrame to avoid further errors

    # Define the initial columns
    initial_columns = ['Ramses_id', 'Quote_name', 'Quote_measured_value', 'Quote_category', 'Quote_State', 'Date_control']

    if initial_columns_only:
        df = df[initial_columns]
    else:
        additional_columns = [
            'Corrected_value', 'Branch', 'Nominal_value', 'IAL_min', 'IAL_max', 'IL_min', 'IL_max', 'AL_min', 'AL_max',
            'NEW_min', 'NEW_max', 'MAI_min', 'MAI_max', 'Quote_name_general', 'Num_ES', 'Cat_UIC', 'Stratégie', 
            'Type_AW', 'Switch_family', 'Tangent_hart', 'Déviation', 'V_directe', 'V_déviée', 'Faisceau', 
            'Date_dernier_renouv', 'Coeur_fissuré', 'Gare_Bifurcation', 'Ligne', 'Cat_voie', 'Voie', 
            'Wissel_begin', 'Wisselzone_begin', 'Wissel_einde', 'Wisselzone_einde', 'Wissel_begin_KP', 'Wissel_begin_M', 
            'Wissel_einde_KP', 'Wissel_einde_M', 'Wisselzone_begin_KP', 'Wisselzone_begin_M', 'Wisselzone_einde_KP', 
            'Wisselzone_einde_M', 'Modèle_P1', 'Modèle_P2', 'Nombre_att_compl', 'Rayon_directe', 'Straal_afwijkende_tak', 
            'Nom_verkanting', 'Model_halve_tongenstellen', 'Modèle_K1_K2', 'Arr', 'Poste',
            'Date_last_control', 'Type_control', 'Tool_id', 'Périodicité', 'Author'
        ]
        df = df[initial_columns + additional_columns]

    # Sort the DataFrame by Ramses_id, Quote_name, and Date_control
    df = df.sort_values(by=['Ramses_id', 'Quote_name', 'Date_control'])

    # Limit the DataFrame to the specified number of rows
    df = df.head(limit)

    # Cache the result for 1 hour
    cache.set(cache_key, df, 3600)

    return df
