import asyncio
import aiohttp
from colorama import Fore, Style, init
import os
from lxml import html
import aiofiles
import hashlib
from keyauth import api
import sys

os.system("title Code Created By Kayy / Discord.gg/KayyShop")

init(autoreset=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    )
}

SEM = asyncio.Semaphore(1000)

async def verificar_nombre_usuario_telegram(session, username):
    url = f"https://t.me/{username}"
    
    try:
        async with SEM:
            async with session.get(url, headers=HEADERS, timeout=10) as respuesta:
                if respuesta.status == 200:
                    contenido = await respuesta.text()
                    return "tgme_page_extra" in contenido
                else:
                    return False
    except aiohttp.ClientError:
        return False
    except asyncio.TimeoutError:
        return False

async def verificar_nombre_usuario_fragment(session, username):
    url_username = f"https://fragment.com/username/{username}"
    
    try:
        async with SEM:
            async with session.get(url_username, headers=HEADERS, timeout=10) as respuesta_username:
                if respuesta_username.status == 404:
                    return True
                elif respuesta_username.status == 200:
                    url_search = f"https://fragment.com/?query={username}"
                    async with session.get(url_search, headers=HEADERS, timeout=10) as respuesta_search:
                        if respuesta_search.status != 200:
                            return False
                        contenido = await respuesta_search.text()
                        tree = html.fromstring(contenido)
                        elementos = tree.xpath("/html/body/div[2]/main/section[2]/div[2]/table/tbody/tr/td[2]/div/div[1]")
                        return not elementos
                else:
                    return False
    except aiohttp.ClientError:
        return False
    except asyncio.TimeoutError:
        return False
    except Exception as e:
        print(f"{Fore.YELLOW}Error al verificar Fragment para '{username}': {e}{Style.RESET_ALL}")
        return False

async def procesar_usuario(session, username, vf, ivf, lock):
    username = username.strip()
    if not username:
        print(f"{Fore.YELLOW}Nombre de usuario vacío. Saltando...{Style.RESET_ALL}")
        return
    
    es_valido_telegram = await verificar_nombre_usuario_telegram(session, username)
    if es_valido_telegram:
        mensaje = f"[-] No disponible en Telegram: {Fore.RED}{username}{Style.RESET_ALL}"
        resultado = ('invalidos', username)
    else:
        es_disponible_fragment = await verificar_nombre_usuario_fragment(session, username)
        if es_disponible_fragment:
            mensaje = f"[-] No disponible en Telegram: {Fore.RED}{username}{Style.RESET_ALL}"
            resultado = ('validos', username)
        else:
            mensaje = f"[+] Disponible: {Fore.GREEN}{username}{Style.RESET_ALL}"
            resultado = ('invalidos', username)
    
    print(mensaje)
    
    async with lock:
        if resultado[0] == 'validos':
            await vf.write(resultado[1] + '\n')
        else:
            await ivf.write(resultado[1] + '\n')

async def main_async():
    nombre_archivo = "comprobar.txt"
    validos = "validos.txt"
    invalidos = "invalidos.txt"
    
    if not os.path.isfile(nombre_archivo):
        print(f"{Fore.RED}El archivo '{nombre_archivo}' no existe. Por favor, crea el archivo y agrega los nombres de usuario a verificar.{Style.RESET_ALL}")
        return
    
    try:
        async with aiofiles.open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            lineas = await archivo.readlines()
    except Exception as e:
        print(f"{Fore.RED}Error al leer el archivo '{nombre_archivo}': {e}{Style.RESET_ALL}")
        return
    
    if not lineas:
        print(f"{Fore.YELLOW}El archivo '{nombre_archivo}' está vacío. Por favor, agrega nombres de usuario para verificar.{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Iniciando la verificación de nombres de usuario desde '{nombre_archivo}'...{Style.RESET_ALL}\n")
    
    async with aiofiles.open(validos, 'w', encoding='utf-8') as vf, \
               aiofiles.open(invalidos, 'w', encoding='utf-8') as ivf:
        lock = asyncio.Lock()
        async with aiohttp.ClientSession() as session:
            tareas = [
                procesar_usuario(session, linea, vf, ivf, lock)
                for linea in lineas
            ]
            await asyncio.gather(*tareas, return_exceptions=True)
    
    print(f"\n{Fore.CYAN}Verificación completada '{validos}' e '{invalidos}'.{Style.RESET_ALL}")
    

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
    input("\nPulsa Enter para finalizar...")
    
