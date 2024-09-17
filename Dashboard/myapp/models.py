from django.db import models
from django.db import connection
import logging
import pandas as pd

class CompleteFinalCleanedData(models.Model):
    django_index = models.AutoField(primary_key=True)
    Quote_name = models.TextField(db_index=True)
    Quote_measured_value = models.FloatField(db_index=True)
    Corrected_value = models.FloatField()
    Branch = models.IntegerField()
    Nominal_value = models.FloatField()
    IAL_min = models.FloatField()
    IAL_max = models.FloatField()
    IL_min = models.FloatField()
    IL_max = models.FloatField()
    AL_min = models.FloatField()
    AL_max = models.FloatField()
    NEW_min = models.FloatField()
    NEW_max = models.FloatField()
    MAI_min = models.FloatField()
    MAI_max = models.FloatField()
    Quote_category = models.TextField(db_index=True)
    Quote_State = models.TextField(db_index=True)
    Quote_name_general = models.TextField()
    Num_ES = models.CharField(db_column='Numéro ES', max_length=255)
    Cat_UIC = models.CharField(db_column='Catégorie UIC', max_length=255)
    Stratégie = models.TextField()
    Type_AW = models.TextField(db_column="Type d'appareil")
    Switch_family = models.TextField()
    Tangent_hart = models.TextField()
    Déviation = models.TextField()
    V_directe = models.CharField(db_column='Vitesse branche directe', max_length=255)
    V_déviée = models.CharField(db_column='Vitesse branche déviée', max_length=255)
    Faisceau = models.TextField()
    Date_dernier_renouv = models.DateTimeField()
    Coeur_fissuré = models.TextField(db_column='Coeur(s) fissuré(s)')
    Gare_Bifurcation = models.TextField(db_column='Gare / Bifurcation')
    Ligne = models.TextField()
    Cat_voie = models.TextField(db_column='Catégorie de voie')
    Voie = models.CharField(max_length=255)
    Wissel_begin = models.CharField(max_length=255)
    Wisselzone_begin = models.CharField(max_length=255)
    Wissel_einde = models.CharField(max_length=255)
    Wisselzone_einde = models.CharField(max_length=255)
    Wissel_begin_KP = models.CharField(max_length=255)
    Wissel_begin_M = models.CharField(max_length=255)
    Wissel_einde_KP = models.CharField(max_length=255)
    Wissel_einde_M = models.CharField(max_length=255)
    Wisselzone_begin_KP = models.CharField(max_length=255)
    Wisselzone_begin_M = models.CharField(max_length=255)
    Wisselzone_einde_KP = models.CharField(max_length=255)
    Wisselzone_einde_M = models.CharField(max_length=255)
    Modèle_P1 = models.CharField(db_column='Modèle coeur P1', max_length=255)
    Modèle_P2 = models.CharField(db_column='Modèle coeur P2', max_length=255)
    Nombre_att_compl = models.CharField(db_column="Nombre d'attaques compl.", max_length=255)
    Rayon_directe = models.CharField(db_column='Rayon voie directe', max_length=255)
    Straal_afwijkende_tak = models.CharField(max_length=255)
    Nom_verkanting = models.CharField(db_column='Nominale verkanting', max_length=255)
    Model_halve_tongenstellen = models.TextField(db_column='Model halve tongenstellen')
    Modèle_K1_K2 = models.TextField(db_column='Modèle coeur K1/K2')
    Arr = models.IntegerField(db_column='Arrond.:')
    Poste = models.IntegerField(db_column='Poste:')
    Ramses_id = models.TextField(db_column='No. Ident.', db_index=True)
    Date_control = models.DateTimeField(db_column='Date de contrôle', db_index=True)
    Date_last_control = models.DateTimeField(db_column='Date dernier contrôle')
    Type_control = models.TextField(db_column='Type de contrôle')
    Tool_id = models.CharField(db_column='Règle 1', max_length=255)
    Périodicité = models.IntegerField(db_column='Périodicité')
    Author = models.TextField(db_column='Fiche remplie par:')
    Date_validation_SMS = models.TextField(db_column='Date validation SMS', default=' ')
    Path = models.TextField()

    class Meta:
        abstract = True

    

class DynamicTableLoader:
    @staticmethod
    def load_data(year, arrondissement):
        table_name = f'"cleaned_data_{str(year)}.0_arr_{str(arrondissement)}"'
        query = f"SELECT * FROM {table_name}"

        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=columns)

        # Log the DataFrame shape and column names
        logging.info(f"Loaded data from {table_name} with shape {df.shape}")
        logging.info(f"Columns: {df.columns.tolist()}")
        logging.info(f"Sample Data:\n{df.head()}")

        return columns, rows
    
