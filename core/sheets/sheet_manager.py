"""
AI JOB FOUNDRY - Google Sheets Manager
Maneja todas las operaciones con Google Sheets

Autor: Marcos Alvarado
Fecha: 2025-11-13
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]

class SheetManager:
    """Gestor de Google Sheets"""
    
    def __init__(self):
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.credentials = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials)
        
        # Nombres de pestañas
        self.tabs = {
            "registry": "Registry",
            "linkedin": "LinkedIn",
            "indeed": "Indeed",
            "glassdoor": "Glassdoor",
            "resumen": "Resumen"
        }
    
    def _get_credentials(self):
        """Obtiene credenciales OAuth de Google"""
        creds = None
        token_path = "data/credentials/token.json"
        credentials_path = "data/credentials/credentials.json"
        
        # Token guardado previamente
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # Si no hay credenciales válidas, autenticar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Guardar credenciales
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def get_all_jobs(self, tab: str = "registry") -> List[Dict]:
        """
        Obtiene todas las ofertas de una pestaña
        
        Args:
            tab: Nombre de pestaña (registry, linkedin, indeed, glassdoor)
        
        Returns:
            Lista de diccionarios con ofertas
        """
        tab_name = self.tabs.get(tab, "Registry")
        
        # Leer toda la pestaña
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{tab_name}!A1:Z1000"  # Leer hasta 1000 filas
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return []
        
        # Primera fila = headers
        headers = values[0]
        
        # Convertir a lista de dicts
        jobs = []
        for row in values[1:]:
            # Rellenar con vacíos si faltan columnas
            row_data = row + [''] * (len(headers) - len(row))
            job = dict(zip(headers, row_data))
            jobs.append(job)
        
        return jobs
    
    def append_rows(self, tab: str, rows: List[List]) -> bool:
        """
        Agrega múltiples filas al Sheet
        
        Args:
            tab: Nombre de la pestaña (ej: "Jobs", "LinkedIn")
            rows: Lista de listas con valores [[val1, val2], [val1, val2]]
        
        Returns:
            True si exitoso
        """
        try:
            # Si el tab no existe en self.tabs, úsalo directamente
            tab_name = self.tabs.get(tab.lower(), tab)
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{tab_name}!A2",  # Después de headers
                valueInputOption="USER_ENTERED",
                body={"values": rows}
            ).execute()
            
            return True
        except Exception as e:
            print(f"❌ Error appending rows: {e}")
            return False


    def add_job(self, job_data: Dict, tab: str = "registry") -> bool:
        """
        Agrega una nueva oferta al Sheet
        
        Args:
            job_data: Diccionario con datos de la oferta
            tab: Pestaña donde agregar
        
        Returns:
            True si exitoso
        """
        tab_name = self.tabs.get(tab, "Registry")
        
        # Obtener headers
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{tab_name}!A1:Z1"
        ).execute()
        
        headers = result.get('values', [[]])[0]
        
        if not headers:
            raise Exception(f"No se encontraron headers en {tab_name}")
        
        # Crear fila con valores en el orden correcto
        row = []
        for header in headers:
            value = job_data.get(header, "")
            row.append(str(value) if value else "")
        
        # Agregar fila
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"{tab_name}!A2",  # Después de headers
            valueInputOption="USER_ENTERED",
            body={"values": [row]}
        ).execute()
        
        return True
    
    def update_job(self, row_id: int, updates: Dict, tab: str = "registry") -> bool:
        """
        Actualiza una oferta existente
        
        Args:
            row_id: Número de fila (2 = primera oferta)
            updates: Diccionario con columnas a actualizar
            tab: Pestaña
        
        Returns:
            True si exitoso
        """
        tab_name = self.tabs.get(tab, "Registry")
        
        # Obtener headers
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{tab_name}!A1:Z1"
        ).execute()
        
        headers = result.get('values', [[]])[0]
        
        # Actualizar columnas específicas
        for column_name, value in updates.items():
            if column_name in headers:
                col_index = headers.index(column_name)
                col_letter = chr(65 + col_index)  # A=0, B=1, etc.
                
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{tab_name}!{col_letter}{row_id}",
                    valueInputOption="USER_ENTERED",
                    body={"values": [[str(value)]]}
                ).execute()
        
        return True
    
    def batch_update_jobs(self, updates: List[Dict]) -> bool:
        """
        Actualiza múltiples ofertas en una sola request (más eficiente)
        
        Args:
            updates: Lista de dicts con {'row_id', 'tab', 'updates'}
        
        Returns:
            True si exitoso
        """
        data = []
        
        for update_item in updates:
            row_id = update_item['row_id']
            tab = update_item.get('tab', 'registry')
            tab_name = self.tabs.get(tab, "Registry")
            updates_dict = update_item['updates']
            
            # Obtener headers de esta pestaña (podría cachear esto)
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{tab_name}!A1:Z1"
            ).execute()
            
            headers = result.get('values', [[]])[0]
            
            # Crear updates para batch
            for column_name, value in updates_dict.items():
                if column_name in headers:
                    col_index = headers.index(column_name)
                    col_letter = chr(65 + col_index)
                    
                    data.append({
                        'range': f"{tab_name}!{col_letter}{row_id}",
                        'values': [[str(value)]]
                    })
        
        # Batch update
        if data:
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    'valueInputOption': 'USER_ENTERED',
                    'data': data
                }
            ).execute()
        
        return True
    
    def find_job_by_url(self, url: str, tab: str = "registry") -> Optional[Dict]:
        """
        Busca una oferta por su URL
        
        Args:
            url: URL de la oferta
            tab: Pestaña donde buscar
        
        Returns:
            Dict con oferta o None
        """
        jobs = self.get_all_jobs(tab)
        
        for job in jobs:
            if job.get('ApplyURL') == url:
                return job
        
        return None
    
    def get_jobs_by_status(self, status: str, tab: str = "registry") -> List[Dict]:
        """
        Filtra ofertas por estado
        
        Args:
            status: Status a filtrar (Scraped, Applied, Interview, etc.)
            tab: Pestaña
        
        Returns:
            Lista de ofertas con ese status
        """
        jobs = self.get_all_jobs(tab)
        return [job for job in jobs if job.get('Status') == status]
    
    def update_job_status(self, row_index: int, new_status: str, tab: str = "registry") -> bool:
        """
        Actualiza el status de una oferta
        
        Args:
            row_index: Índice de la fila (1-based, incluye header)
            new_status: Nuevo status (New, Applied, Expired, Interview, Rejected)
            tab: Pestaña donde actualizar
        
        Returns:
            True si exitoso
        """
        tab_name = self.tabs.get(tab, "Registry")
        
        # Get headers to find Status column
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{tab_name}!A1:Z1"
        ).execute()
        
        headers = result.get('values', [[]])[0]
        
        if 'Status' not in headers:
            print(f"⚠️  Warning: Status column not found in {tab_name}")
            return False
        
        status_col_index = headers.index('Status')
        status_col_letter = chr(65 + status_col_index)
        
        # Update status
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=f"{tab_name}!{status_col_letter}{row_index}",
            valueInputOption='USER_ENTERED',
            body={'values': [[new_status]]}
        ).execute()
        
        return True
    
    def test_connection(self):
        """Test rápido de conexión"""
        print("\n" + "="*70)
        print("🧪 TESTING CONEXIÓN A GOOGLE SHEETS")
        print("="*70 + "\n")
        
        try:
            # Intentar leer Registry
            jobs = self.get_all_jobs("registry")
            print(f"✅ Conexión exitosa")
            print(f"   📊 {len(jobs)} ofertas en Registry")
            
            if jobs:
                print(f"   📝 Última oferta: {jobs[-1].get('Company', 'N/A')}")
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

# Test si se ejecuta directamente
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    manager = SheetManager()
    manager.test_connection()
