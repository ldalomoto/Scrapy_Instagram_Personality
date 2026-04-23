import os #interactual con el sistema
import random #numeros aleatorios
import time #manejar el tiempo
import requests #hacer peticiones
from fake_useragent import UserAgent #simular un navegador
import csv #archivos cvs
import concurrent.futures #manejar la concurrencia

# ID de sesión de Instagram para autenticación
SESSION_ID = "6666325872%3AJ5G6WtBVqRGeOZ%3A24%3AAYgy_dwYEmhpHd9WU1M1ouRXBHEXXMatoiiZGuchkw"

def get_user_details(username, session_id):
    """
    Obtiene los detalles básicos de un usuario de Instagram
    
    Args:
        username (str): Nombre de usuario de Instagram
        session_id (str): ID de sesión para autenticación
    
    Returns:
        dict: Diccionario con información del usuario o None si hay error
    """
    # Headers para simular una petición real del navegador
    headers = {
        "authority": "www.instagram.com",
        "referer": f"https://www.instagram.com/{username}/",
        "user-agent": UserAgent().random,  # User agent aleatorio
        'x-ig-app-id': '936619743392459',  # ID de la app de Instagram
        "x-requested-with": "XMLHttpRequest"
    }
    
    # Cookies de autenticación
    cookies = {'sessionid': session_id}
    # URL de la API de Instagram para obtener información del perfil
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    try:
        # Realizar petición GET a la API
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        
        # Si la petición fue exitosa
        if response.status_code == 200:
            data = response.json()  # Convertir respuesta a JSON
            
            # Extraer datos del usuario
            user_data = data.get('data', {}).get('user', {})
            
            # Retornar información relevante del usuario
            return {
                'user_id': user_data.get('id'),  # ID único del usuario
                'username': user_data.get('username'),  # Nombre de usuario
                'follower_count': user_data.get('edge_followed_by', {}).get('count', 0),  # Número de seguidores
                'following_count': user_data.get('edge_follow', {}).get('count', 0)  # Número de seguidos
            }
    except Exception as e:
        print(f"Error obteniendo detalles de {username}: {e}")
    
    return None

def get_all_followers_list(target_username, session_id):
    """
    Obtiene la lista completa de seguidores de un usuario
    
    Args:
        target_username (str): Usuario objetivo a scrapear
        session_id (str): ID de sesión para autenticación
    
    Returns:
        tuple: (lista_de_seguidores, información_del_objetivo)
    """
    
    # Obtener información básica del usuario objetivo
    target_info = get_user_details(target_username, session_id)
    if not target_info:
        print("No se pudo obtener información del usuario objetivo")
        return [], None
    
    # MOSTRAR TANTO SEGUIDORES COMO SEGUIDOS
    print(f"Objetivo: @{target_info['username']} - {target_info['follower_count']} seguidores - {target_info['following_count']} seguidos")
    
    # Verificar si el usuario tiene seguidores
    if target_info['follower_count'] == 0:
        print("El usuario no tiene seguidores")
        return [], target_info
    
    all_followers = []  # Lista para almacenar todos los seguidores
    max_id = None  # ID para paginación
    page_count = 0  # Contador de páginas
    
    print("Iniciando scraping de seguidores...")
    
    # Bucle para obtener todos los seguidores (paginación)
    while len(all_followers) < target_info['follower_count']:
        try:
            # Parámetros para la petición
            params = {'count': '50', 'search_surface': 'follow_list_page'}
            if max_id:
                params['max_id'] = max_id  # Agregar max_id si existe para paginación
            
            # Headers para la petición
            headers = {
                'accept': '*/*',
                'referer': f'https://www.instagram.com/{target_username}/followers/',
                'user-agent': UserAgent().random,
                'x-ig-app-id': '936619743392459',
                'x-requested-with': 'XMLHttpRequest',
            }
            
            cookies = {'sessionid': session_id}
            # URL de la API para obtener seguidores
            url = f'https://www.instagram.com/api/v1/friendships/{target_info["user_id"]}/followers/'
            
            # Realizar petición
            response = requests.get(url, headers=headers, cookies=cookies, params=params, timeout=30)
            
            # Verificar si la petición fue exitosa
            if response.status_code != 200:
                print(f"Error HTTP {response.status_code} al obtener seguidores")
                break
            
            data = response.json()  # Convertir respuesta a JSON
            
            # Extraer lista de usuarios
            users = data.get('users', [])
            
            # Si no hay más usuarios, terminar
            if not users:
                print("No se encontraron más seguidores")
                break
            
            # Agregar usernames a la lista
            for user in users:
                if user.get('username'):
                    all_followers.append(user.get('username'))
            
            page_count += 1
            print(f"Página {page_count}: {len(users)} seguidores obtenidos - Total: {len(all_followers)}/{target_info['follower_count']}")
            
            # Verificar si hay más páginas
            if not data.get('next_max_id') or not data.get('big_list', True):
                print("Fin de la lista de seguidores")
                break
            
            # Actualizar max_id para la siguiente página
            max_id = data.get('next_max_id')
            # Esperar entre peticiones para evitar ser bloqueado
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"Error en paginación: {e}")
            break
    
    print(f"Total de seguidores obtenidos: {len(all_followers)}")
    return all_followers, target_info

def process_follower_batch(followers_batch, session_id, batch_num, total_batches):
    """
    Procesa un lote de seguidores para obtener sus detalles
    
    Args:
        followers_batch (list): Lista de usernames a procesar
        session_id (str): ID de sesión para autenticación
        batch_num (int): Número del lote actual
        total_batches (int): Total de lotes
    
    Returns:
        list: Lista de diccionarios con información de los seguidores
    """
    
    batch_data = []  # Datos del lote actual
    processed_count = 0  # Contador de procesados
    
    # Procesar cada seguidor en el lote
    for follower_username in followers_batch:
        # Obtener información del seguidor
        follower_info = get_user_details(follower_username, session_id)
        if follower_info:
            # Agregar información relevante
            batch_data.append({
                'username': follower_info['username'],
                'follower_count': follower_info['follower_count'],
                'following_count': follower_info['following_count']
            })
            processed_count += 1
            
            # Mostrar progreso cada 5 procesados
            if processed_count % 5 == 0:
                print(f"   Lote {batch_num}/{total_batches}: {processed_count}/{len(followers_batch)} procesados")
        
        # Esperar entre peticiones para evitar ser bloqueado
        time.sleep(random.uniform(0.5, 1.5))
    
    print(f"Lote {batch_num}/{total_batches} completado: {len(batch_data)} seguidores procesados")
    return batch_data

def split_list_into_chunks(lst, num_chunks):
    """
    Divide una lista en chunks aproximadamente del mismo tamaño
    
    Args:
        lst (list): Lista a dividir
        num_chunks (int): Número de chunks a crear
    
    Returns:
        list: Lista de chunks
    """
    
    # Si la lista está vacía, retornar chunks vacíos
    if len(lst) == 0:
        return [[] for _ in range(num_chunks)]
    
    # Calcular tamaño promedio de cada chunk
    avg = len(lst) // num_chunks
    remainder = len(lst) % num_chunks  # Resto para distribuir
    
    chunks = []  # Lista de chunks
    start = 0    # Índice inicial
    
    # Crear cada chunk
    for i in range(num_chunks):
        # Calcular fin del chunk (distribuir el resto en los primeros chunks)
        end = start + avg + (1 if i < remainder else 0)
        chunks.append(lst[start:end])  # Agregar chunk
        start = end  # Actualizar inicio para siguiente chunk
    
    return chunks

def scrape_followers_parallel(target_username, session_id, num_threads):
    """
    Realiza el scraping de seguidores usando múltiples hilos
    
    Args:
        target_username (str): Usuario objetivo a scrapear
        session_id (str): ID de sesión para autenticación
        num_threads (int): Número de hilos a usar
    
    Returns:
        list: Lista con todos los datos obtenidos
    """
    
    print(f"Iniciando scraping paralelo con {num_threads} hilos...")
    
    # Obtener todos los seguidores del usuario objetivo
    all_followers, target_info = get_all_followers_list(target_username, session_id)
    
    # Verificar si se obtuvieron seguidores
    if not all_followers or not target_info:
        print("No se pudieron obtener seguidores")
        return []
    
    # Inicializar lista de datos con el usuario objetivo
    all_data = [{
        'username': target_info['username'],
        'follower_count': target_info['follower_count'],
        'following_count': target_info['following_count']
    }]
    
    # Dividir seguidores en chunks para procesamiento paralelo
    follower_chunks = split_list_into_chunks(all_followers, num_threads)
    
    print(f"Dividiendo {len(all_followers)} seguidores en {num_threads} lotes...")
    
    # Usar ThreadPoolExecutor para procesamiento paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []  # Lista de futuros (tareas asíncronas)
        
        # Enviar cada chunk a un hilo diferente
        for i, chunk in enumerate(follower_chunks):
            if chunk:  # Solo si el chunk no está vacío
                print(f"Iniciando lote {i+1}/{len(follower_chunks)} con {len(chunk)} seguidores")
                # Enviar tarea al executor
                future = executor.submit(process_follower_batch, chunk, session_id, i+1, len(follower_chunks))
                futures.append(future)
        
        # Recolectar resultados de los hilos
        completed_count = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                batch_data = future.result()  # Obtener resultado del hilo
                all_data.extend(batch_data)   # Agregar a datos totales
                completed_count += 1
                print(f"Progreso general: {completed_count}/{len(futures)} lotes completados")
            except Exception as e:
                print(f"Error en lote: {e}")
                completed_count += 1
    
    print(f"Scraping completado. Total de perfiles obtenidos: {len(all_data)}")
    return all_data

def save_to_csv(data, filename):
    """
    Guarda los datos en un archivo CSV
    
    Args:
        data (list): Lista de diccionarios con datos
        filename (str): Nombre del archivo
    """
    try:
        # Crear directorio si no existe
        os.makedirs('PROFILES_DATA', exist_ok=True)
        filepath = os.path.join('PROFILES_DATA', filename)

        # Escribir datos en CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['username', 'follower_count', 'following_count'])
            writer.writeheader()  # Escribir encabezados
            writer.writerows(data)  # Escribir datos
        
        print(f"Datos guardados en: {filepath}")
        
    except Exception as e:
        print(f"Error guardando CSV: {e}")

def main():
    """
    Función principal que coordina todo el proceso de scraping
    """
    
    # Solicitar username objetivo
    target_username = input("Ingresa el username de Instagram a scrapear: ").strip()
    
    # Verificar que se ingresó un username
    if not target_username:
        print("No se ingresó username")
        return
    
    # Solicitar número de hilos
    num_threads = int(input(f"Número de hilos a usar: "))
    
    print(f"\nIniciando scraping de @{target_username}...")
    
    # Realizar scraping paralelo
    all_data = scrape_followers_parallel(target_username, SESSION_ID, num_threads)
    
    # Verificar si se obtuvieron datos
    if not all_data or len(all_data) <= 1:
        print("No se obtuvieron datos suficientes")
        return

    # Mostrar resumen de resultados
    print(f"\nRESULTADOS:")
    print(f"   • Perfiles obtenidos: {len(all_data)}")
    print(f"   • Usuario objetivo: @{all_data[0]['username']}")
    print(f"   • Seguidores objetivo: {all_data[0]['follower_count']}")
    print(f"   • Seguidos objetivo: {all_data[0]['following_count']}")
    print(f"   • Seguidores scrapeados: {len(all_data) - 1}")
    
    # Guardar datos en CSV
    filename = f"{target_username}_followers.csv"
    save_to_csv(all_data, filename)

# Punto de entrada del programa
if __name__ == "__main__":
    main()