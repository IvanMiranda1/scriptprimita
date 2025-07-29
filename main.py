from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import traceback
import sys
import os
from dotenv import load_dotenv
load_dotenv()

options = Options()

#options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.get("https://personal.seguridadciudad.gob.ar/eventuales/Default.aspx")

#Funciones
def enviar_mensaje_x_telegram(mensaje):
    token = os.getenv("API_TOKEN")
    chat_ids = ["1277417811","5581335992"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for chat_id in chat_ids:
        data = {"chat_id": chat_id, "text": mensaje}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Mensaje enviado correctamente")
        else:
            print("Error al enviar mensaje")
def checkboxConfirm():
    try:

        checkbox = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "chkConfirmaLectura")))
        if checkbox.is_displayed() and checkbox.is_enabled():
            is_checked = driver.execute_script("return arguments[0].checked;", checkbox)
            if not is_checked:
                checkbox.click()
            else:
                #print("Esta marcado, entonces tengo que clickear 2 veces")
                checkbox.click()
                checkbox.click()
        try:
            cerrar = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "btnCerrarModal")))
            cerrar.click()
        except:
            print("No fue posible encontrar el btnCerrarModal")
    except Exception as e:
        print(f"Error intentando confirmar checkbox: {str(e)}")

def mensajepriv(mensaje):
    token = os.getenv("API_TOKEN")
    chat_id = "1277417811"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": mensaje}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Mensaje enviado correctamente")
    else:
            print("Error al enviar mensaje")
def login():
    try:
        username = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "txtUsuario")))
        password = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "txtClave")))
        
        username.send_keys(os.getenv("USERNAME"))
        password.send_keys(os.getenv("PASSWORD"))   
        password.send_keys(Keys.RETURN)
    except Exception as e:
        print(f"❌ Error al intentar iniciar sesión: {str(e)}")
        mensajepriv("⚠️ Error al intentar iniciar sesión en la aplicación.")
        return False
    return True
def esperar_carga():
    """"Verifica que la pagina se haya cargado correctamente"""
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "id"))) #Un elemento clave de la pagina cuando SI cargo!
        return True
    except:
        return False

mensajepriv("¡Bot encendido! 🐕")
print("Encendido!")

stateSelenium1 = False
stateSelenium2 = False

### Main
while True:
    try:
        if login():
            #confirmacion del checkbox
            checkboxConfirm()

            time.sleep(10)

            while True:
                #buscar plazas disponibles
                print("1")
                links = driver.find_elements(By.XPATH, "//td[@class='boton-grilla']//a")
                if not links:
                    print("No se encontraron plazas disponibles.")
                    time.sleep(10)
                    driver.refresh()  
                    time.sleep(5)  

                    # Verificar si estamos en la pantalla de login
                    if "login" in driver.current_url.lower():  
                        print("🔑 Se detectó pantalla de login, volviendo a iniciar sesión...")
                        login()  # Llamar a la función que realiza el login
                        
                    continue

                checkboxConfirm()
                print("2")

                try:
                    for link in links:
                        print("3 - Analizando botón:", link.text)
                        if "INFANTES" in link.text:
                            print("Se encontró un botón para INFANTES")
                            print(f"link.is_enable = {link.is_enabled()}")
                            if not link.is_enabled():
                                print("⚠️ Botón INFANTES está bloqueado (deshabilitado).")
                                continue  # Saltar al siguiente botón
                            try:
                                print("4")
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(link)).click()
                                print("✅ Se hizo click en el botón INFANTES.")
                                print("5")
                                time.sleep(3)

                                # link.click() ## aca me da error
                                # time.sleep(6)
                                try:
                                    print("6, intento de click a boton de confirmar postulacion ((si, error? entonces el boton existe pero la plaza estan llenas))")
                                    WebDriverWait(driver, 10).until(
                                    EC.visibility_of_element_located((By.ID, "modConfirmaPPostulacion"))
                                    )
                                    print("7")
                                    enviar_mensaje_x_telegram("¡Inscribite a la plaza! 🐕")
                                    print("Mensaje enviado a telegram")
                                except Exception as e:
                                    print(f"7.5 No se pudo encontrar el modal de confirmación: {str(e)}")
                                    
                            except:
                                print("Boton INFANTES bloqueado!")
                except:
                    print("❌ Error en la búsqueda de plazas.")
                    stateSelenium1 = True

                #Refresh de seccion de plazas
                #print("Esperando 30 minutos para refrescar la pagina")
                #time.sleep(1800)# media hora

                print("Esperando 20 minutos para refrescar la pagina")
                time.sleep(1200)# diez minutos

                print("8,'try'se intenta, espera 10 segundos mientras busca la presencia del elemento que es el boton actualizar")
                try:
                    WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_btnRefrescarGrillaEventos"))
                    )
                    print("9, busca el boton de refrescar solo la parte de las plazas y le da click")
                    refrescar_seccion_plazas = driver.find_element(By.ID, "ContentPlaceHolder1_btnRefrescarGrillaEventos")
                    refrescar_seccion_plazas.click()
                    print("Refrescando seccion de plazas... se esperan 20 segundos")
                    time.sleep(20)
                except Exception as e:
                    print("🔄 Refrescando pagia completa...")
                    try:
                        driver.refresh()  # Intentar refrescar la página
                        time.sleep(30)  # Dar tiempo para que cargue todo
                        print("✅ Página refrescada correctamente")
                        stateSelenium2 = False  # El refresh se hizo correctamente, no hay fallo
                    except Exception as e:
                        print(f"9.5 ⚠️ No se pudo refrescar la sección de plazas: {str(e)}")
                        stateSelenium2 = True  # ⚠️ Marca fallo crítico si falla el refresh
                    
                if stateSelenium1 and stateSelenium2:
                    stateSelenium1 = False 
                    stateSelenium2 = False
                    print("🚨 ERROR CRÍTICO: Ambos fallos detectados. Reiniciando script...")
                    #raise Exception("Reinicio forzado por fallo crítico.")
                    driver.quit()
                    time.sleep(30)
                    driver = webdriver.Firefox(options=options)
                    driver.get("https://personal.seguridadciudad.gob.ar/eventuales/Default.aspx")
                    continue 


    except Exception as e: #si se detiene la aplicacion
        error_msg = f"❌ Error en el bot: {str(e)}\n{traceback.format_exc()}"
        print("Dio error el main.")
        print(error_msg)
        mensajepriv(error_msg)
        mensajepriv("Reiniciando bot 🤖")
        sys.exit(1)  # Detiene la ejecución

     # 🔄 En lugar de salir, cerrar el navegador y reintentar
        driver.quit()
        time.sleep(30)
        driver = webdriver.Firefox(options=options)
        driver.get("https://personal.seguridadciudad.gob.ar/eventuales/Default.aspx")  # Reabrir navegador
        # driver.save_screenshot() #sirve para sacar screenshot, puedo usarlo para capturar el momento en el que da error
