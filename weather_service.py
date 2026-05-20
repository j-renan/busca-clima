import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Union

def fahrenheit_to_celsius(f: float) -> float:
    """Converte Fahrenheit para Celsius."""
    return round((f - 32) * 5 / 9, 2) if f is not None else None

def mph_to_kmph(mph: float) -> float:
    """Converte Milhas por Hora para Quilômetros por Hora."""
    return round(mph * 1.60934, 2) if mph is not None else None

def validate_city_name(city: str) -> Union[str, None]:
    """Valida o nome da cidade. Retorna None se válido, ou mensagem de erro."""
    if not city or not isinstance(city, str):
        return "O nome da cidade é obrigatório."
    if len(city.strip()) < 2:
        return "O nome da cidade deve ter pelo menos 2 caracteres."
    return None


def transform_weather_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma os dados brutos da API no formato simplificado do dashboard."""
    current = raw_data.get('currentConditions', {})
    days = raw_data.get('days', [])[:7]  # Limitamos a 7 dias
    
    today_str = datetime.now().strftime('%Y-%m-%d')

    
    processed_data = {
        'data': today_str,
        'hora': current.get('datetime'),
        'cidade': raw_data.get('resolvedAddress'),
        'temperatura': fahrenheit_to_celsius(current.get('temp')),
        'umidade': current.get('humidity'),
        'vento': mph_to_kmph(current.get('windspeed')),
        'precipitacao': current.get('precip'),
        'icon': current.get('icon'),
        'previsao': []
    }
    
    for dia in days:
        processed_data['previsao'].append({
            'data': datetime.strptime(dia['datetime'], "%Y-%m-%d").strftime('%d/%m/%Y'),
            'temperatura_max': fahrenheit_to_celsius(dia.get('tempmax')),
            'temperatura_min': fahrenheit_to_celsius(dia.get('tempmin')),
            'umidade': dia.get('humidity'),
            'vento': mph_to_kmph(dia.get('windspeed')),
            'precipitacao': dia.get('precip'),
            'icon': dia.get('icon')
        })
        
    return processed_data

def get_weather_by_city(city: str) -> Dict[str, Any]:
    """
    Função principal (Orquestradora) para buscar dados de clima.
    Aplica validação, busca externa e transformação.
    """
    # 1. Validação
    error_msg = validate_city_name(city)
    if error_msg:
        return {"error": True, "message": error_msg, "status": 400}

    # 2. Preparação da URL
    base_url = os.getenv("BASE_URL_VISUAL_CROSSING")
    api_key = os.getenv("VISUAL_CROSSING_API_KEY")
    
    if not base_url or not api_key:
        return {"error": True, "message": "Configurações de API ausentes.", "status": 500}

    # Definindo intervalo de datas (hoje até daqui a 6 dias)
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d')
    
    url = f"{base_url}{city}/{start_date}/{end_date}?key={api_key}&unitGroup=us&include=days,current"

    # 3. Requisição com tratamento de erros
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            return {"error": True, "message": f"Cidade '{city}' não encontrada.", "status": 404}
        
        response.raise_for_status() # Lança erro para 4xx ou 5xx
        
        data = response.json()
        
        # 4. Transformação
        return {"error": False, "data": transform_weather_data(data), "status": 200}

    except requests.exceptions.Timeout:
        return {"error": True, "message": "Tempo de resposta excedido ao conectar à API de clima.", "status": 504}
    except requests.exceptions.RequestException as e:
        return {"error": True, "message": f"Erro de conexão: {str(e)}", "status": 502}
    except Exception as e:
        return {"error": True, "message": f"Ocorreu um erro inesperado: {str(e)}", "status": 500}
