import time   # Libreria para darle tiempo para iniciar comunicación serial
from tkinter import *  # Interfaz grafica
from PIL import Image, ImageTk     # pillow => el procesamiento de open cv se vea en tkinter
import cv2      # Procesamiento de imagenes
import numpy as np     # Crear matrices
import pyautogui       # Capturar pantalla
import threading        # Generar hilos (multirarea)
from tkinter import PhotoImage
from pathlib import Path    # Acceder a ubicaciones en especifico de la computadora
import os   # Libria del sistema
import speech_recognition as sr # Transforma la voz a texto
import datetime     # Obtener la hora y dia
import pygame       # Para reproducir audios
import serial       # Comunicación serial

# Comunicacion serial

#esp32 = serial.Serial("COM12", 115200,timeout=None)  # Ajusta el puerto COM según tu configuración
time.sleep(2)

# Iniciar tkinter
ventana = Tk()

# Tamaño de la ventana de la computadora

ancho_pantalla = int(ventana.winfo_screenwidth())  # 1920
altura_pantalla = int(ventana.winfo_screenheight())  # 1080
ventana.geometry(f"{int(ancho_pantalla*0.775)}x{int(altura_pantalla*0.93)}+0+0")
ventana.config(bg="gray10")

# Titulo
ventana.title("Auto autónomo")
# No se pueda modificar el tamaño de ventana
ventana.resizable(0, 0)

 # Background

background = Frame(ventana, relief=FLAT,width=int(ancho_pantalla*0.775), height=int(altura_pantalla*0.93),bg="gray10")
background.place(x=0, y=0)

photo_background = PhotoImage(file="background1.png")
fondo = Label(background,image=photo_background,bg="gray10")
fondo.grid(row=0)

# Etiqueta titulo
etiqueta_titulo = Label(ventana, text='Vehículo Autonómo', fg='snow', font=("Franklin Gothic Demi", 22),
                        bg="gray12", width=100)
etiqueta_titulo.place(relx=0.5, rely=0.045, anchor=CENTER)

# Panel camara
ancho_video = 640
altura_video = 480

panel_camara = Frame(ventana, relief=FLAT,bg="snow")
panel_camara.place(x=ancho_pantalla*0.084, y=altura_pantalla*0.125)

# Etiqueta camara

etiqueta_camara = Canvas(ventana, bg="black", width=60, height=333,highlightbackground="white")
etiqueta_camara.place(x=94, y=276)

etiqueta_camara.create_text(33,168, text="Camara del Automóvil", anchor="center", fill="snow",
                                angle=90, font=("Arial", 17, "bold"))

# Coordenadas captura de video

x = int(ancho_pantalla-ancho_pantalla*0.19)
y = int(altura_pantalla*0.12)

width_capture = int(ancho_pantalla*0.19)
height_capture = int(altura_video*0.63)

# Panel objetos

ancho_foto = 640
altura_foto = 480

panel_objetos = Frame(ventana, relief=FLAT,bg="black",width=ancho_foto, height=altura_foto)
panel_objetos.place(x=ancho_pantalla*0.458, y=altura_pantalla*0.415)

# Panel de configuracion

panel_configuracion = Frame(ventana, bd=1, relief=FLAT,width=300, height=100,bg="black")
panel_configuracion.place(x=ancho_pantalla*0.462, y=altura_pantalla*0.22)

# Tablero de la hora

ancho_hora = 500
altura_hora = 60

hora_tablero = Canvas(ventana,width=ancho_hora,height=altura_hora,bg="gray10",highlightbackground='gray10')
hora_tablero.place(x=ancho_pantalla*0.46, y=altura_pantalla*0.13)

# Archivos audios

ubicacion_audios = Path(os.getcwd(),"Audios")

# Redes neuronales entrenadas

alto = cv2.CascadeClassifier('alto.xml')
persona = cv2.CascadeClassifier('persona.xml')
curva = cv2.CascadeClassifier('curva.xml')

# Camara pista

def captura_pantalla():

    # Captura la pantalla y conviértela a un formato que OpenCV pueda manejar
    screenshot = pyautogui.screenshot(region=(x, y, width_capture, height_capture))
    frame = np.array(screenshot)

    # Definir las coordenadas de la región de interés (Camino)
    x2, y2, w2, h2 = int(width_capture*0), int(height_capture * 0.6), int(width_capture*1), int(height_capture * 0.4)
    camino = frame[y2:y2 + h2, x2:x2 + w2]


    return frame,camino
def trasformar_audio_en_texto():

    # almacenar recognizer en variable
    r = sr.Recognizer()

    # configurar el microfono
    with sr.Microphone() as origen:

        # tiempo de espera
        r.pause_threshold = 0.8

        # informar que comenzo la grabacion
        print("ya puedes hablar")

        # guardar lo que escuche como audio
        audio = r.listen(origen)

        try:
            # buscar en google
            pedido = r.recognize_google(audio, language="es-ar")

            # prueba de que pudo ingresar
            print("Dijiste: " + pedido)

            # devolver pedido
            return pedido

        # en caso de que no comprenda el audio
        except sr.UnknownValueError:

            # prueba de que no comprendio el audio
            print("ups, no entendi")

            # devolver error
            return "sigo esperando"

        # en caso de no resolver el pedido
        except sr.RequestError:

            # prueba de que no comprendio el audio
            print("ups, no hay servicio")

            # devolver error
            return "sigo esperando"

        # error inesperado
        except:

            # prueba de que no comprendio el audio
            print("ups, algo ha salido mal")

            # devolver error
            return "sigo esperando"
def reproducir_audio(archivo):

    ruta = Path(ubicacion_audios,archivo)
    # Inicializar pygame
    pygame.init()
    try:
        # Cargar el archivo de audio
        pygame.mixer.music.load(ruta)
        # Reproducir el audio
        pygame.mixer.music.play()
        # Esperar hasta que termine de reproducirse
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error:
        print("No se pudo reproducir el archivo de audio.")
    # Detener pygame
    pygame.quit()

def saludar():

    global momento
    # Momento del dia
    hora = datetime.datetime.now()
    if 5 <= hora.hour < 12:
        reproducir_audio("buenos_dias.mp3")
    elif 12 <= hora.hour < 20:
        reproducir_audio("buenas_tardes.mp3")
    elif 20 <= hora.hour:
        reproducir_audio("buenas_noches.mp3")
def pedir_cosas():

    # variable de corte
    comenzar = True
    reproducir_audio("inicio.mp3")

    # loop central
    while comenzar:

        # activar el micro y guardar el pedido en un string
        pedido = trasformar_audio_en_texto().lower()
        if "cómo estás" in pedido:
            reproducir_audio("como_estas.mp3")
            continue
        elif "hola" in pedido:
            saludar()
            continue
        elif "buenos días" in pedido:
            reproducir_audio("buenos_dias.mp3")
            continue
        elif "buenas tardes" in pedido:
            reproducir_audio("buenas_tardes.mp3")
            continue
        elif "buenas noches" in pedido:
            reproducir_audio("buenas_noches.mp3")
            continue
        elif "preséntate" in pedido:
            reproducir_audio("presentate.mp3")
            continue
        elif "música" in pedido:
            reproducir_audio("reproduciendo.mp3")
            reproducir_audio("cancion1.mp3")
        elif "presentación" in pedido:
            reproducir_audio("presentacion.mp3")
            tarea_auto_var.set(1)
            reproducir_audio("protocolo_presentacion.mp3")
        elif "viaje" in pedido:
            reproducir_audio("viaje.mp3")
            reproducir_audio("parte1_viaje.mp3")
            tarea_auto_var.set(4)
            reproducir_audio("parte2_viaje.mp3")
        elif "suficiente" in pedido:
            tarea_auto_var.set(3)
            reproducir_audio("detener.mp3")
        elif "continúa" in pedido:
            reproducir_audio("continuar.mp3")
            tarea_auto_var.set(4)
        elif "stop" in pedido:
            tarea_auto_var.set(3)
            reproducir_audio("detener.mp3")

        if objetos_var.get() == 1:
            reproducir_audio("señal_alto.mp3")
            objetos_var.set(0)
        elif objetos_var.get() == 2:
            reproducir_audio("señal_curva.mp3")
            objetos_var.set(0)
        elif objetos_var.get() == 3:
            reproducir_audio("persona.mp3")
            objetos_var.set(0)

def mostrar_hora():

    dia = datetime.date.today()

    dia_semana = dia.weekday()

    # diccionario con nombres de los dias
    calendario = {0: "Lunes",
                  1: "Martes",
                  2: "Miércoles",
                  3: "Jueves",
                  4: "Viernes",
                  5: "Sábado",
                  6: "Domingo"}

    # Decidir el dia de la semana

    hora_tablero.delete("text1")
    hora = datetime.datetime.now()
    hora_tiempo = f" {calendario[dia_semana]}      {dia.today()}     {hora.hour}:{hora.minute}:{hora.second}"
    hora_tablero.create_text(ancho_hora * 0.5, altura_hora * 0.55,text=hora_tiempo, fill="snow",font=('Dosis', 15, 'bold'), tags="text1")

def threshold(camino):

    caminoHSV = cv2.cvtColor(camino, cv2.COLOR_BGRA2BGR)

    # Aplicación de mascara color 1
    azulClaro = np.array([int(Hmin.get()), int(Smin.get()), int(Vmin.get())], np.uint8)
    azulOscuro = np.array([int(Hmax.get()), int(Smax.get()), int(Vmax.get())], np.uint8)

    maskBlue = cv2.inRange(caminoHSV, azulClaro, azulOscuro)

    maskBlue = cv2.dilate(maskBlue,kernel,iterations = 1)
    maskBlue = cv2.morphologyEx(maskBlue, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(maskBlue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contador = 0

    cx_1, cy_1, cx_2, cy_2 = 0, 0, 0, 0

    for cnt in contours:

        momentos = cv2.moments(cnt)
        area = momentos['m00']
        if (area > minArea):
            cv2.drawContours(camino, [cnt], 0, (0, 100, 255), -1)
            cx = int(momentos['m10'] / momentos['m00'])
            cy = int(momentos['m01'] / momentos['m00'])
            #cv2.circle(camino, (cx, cy), 10, (0, 0, 255), -1)
            contador += 1
            if contador == 1:
                cx_1 = cx
                cy_1 = cy
            elif contador == 2:
                cx_2 = cx
                cy_2 = cy
                break  # Terminamos el bucle después de encontrar las primeros 2 lineas}

    hx = int(camino.shape[1] / 2.05)
    hy = int(camino.shape[0] / 2)

    cv2.circle(camino, (hx, hy), 20, (0, 0, 255), 3)

    if cx_1 != 0 and cy_1 != 0 and cx_2 != 0 and cy_2 != 0:
        c_x = (cx_1 + cx_2) / 2
        c_y = (cy_1 + cy_2) / 2
        cv2.circle(camino, (int(c_x), int(c_y)), 10, (255, 0, 0), -1)

        c_x = int(c_x)
        h_x = int(hx)

        start_sending_data(c_x,h_x)
        #time.sleep(0.01)

    else:

        start_sending_data(0, 0)
        #time.sleep(0.01)

    return maskBlue
def trafficSignal(frame):


    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    stop_signal = alto.detectMultiScale(gray, 1.01, 10)

    for (x_s, y_s, w_s, h_s) in stop_signal:
        cv2.rectangle(frame, (x_s, y_s), (x_s + w_s, y_s + h_s), (255, 100, 0), 2)
        cv2.putText(frame, f"Alto", (x_s + w_s + 10, y_s + int(h_s/2)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 1, cv2.LINE_AA)
        print(w_s)

        if (w_s > 75):
            tarea_auto_var.set(3)
            objetos_var.set(1)

    turn_left = curva.detectMultiScale(gray, 1.01, 15)

    for (x_t, y_t, w_t, h_t) in turn_left:
        cv2.rectangle(frame, (x_t, y_t), (x_t + w_t, y_t + h_t), (255, 255, 0), 2)
        cv2.putText(frame, f"Curva", (x_t + w_t + 10, y_t + int(h_t / 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1, cv2.LINE_AA)

        if (w_t > 75):
            objetos_var.set(2)

    person = persona.detectMultiScale(gray, 1.01, 10)

    for (x_p, y_p, w_p, h_p) in person:
        cv2.rectangle(frame, (x_p, y_p), (x_p + w_p, y_p + h_p), (0, 255, 100), 2)
        cv2.putText(frame, f"Persona", (x_p + w_p + 10, y_p + int(h_p / 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 1, cv2.LINE_AA)
        print(w_p)
        if (w_p > 115):
            tarea_auto_var.set(3)
            objetos_var.set(3)

    #time.sleep(0.01)
def mostrar_video(imagen,closing):

    # Mostrar video
    imagen = cv2.resize(imagen, (0, 0), fx=1.7, fy=1.7)  # Redimensiona la imagen para hacerla más grande
    img = cv2.cvtColor(imagen, cv2.COLOR_BGRA2BGR)  # cv2.COLOR_BGR2RGB => Transformar a formato BGR
    img = Image.fromarray(img)  # La imagen se convierte en un array de pixeles los cuales ya puede ser manipulados por python
    img.thumbnail((ancho_video, altura_video))  # Redimensionar la imagen
    tkimagen = ImageTk.PhotoImage(img)
    video.configure(image=tkimagen)
    video.image = tkimagen

    closing = cv2.resize(closing, (0, 0), fx=1.4, fy=1.4)  # Redimensiona la imagen para hacerla más grande
    img2 = Image.fromarray(closing)
    img2.thumbnail((ancho_foto, altura_foto))
    tkimage2 = ImageTk.PhotoImage(img2)
    video_umbral.configure(image=tkimage2)
    video_umbral.image = tkimage2

def principal():

    while True:

        mostrar_hora()

        frame,camino = captura_pantalla()   # Capturar pantalla y definir region de interes

        maskBlue = threshold(camino)     # Aplicar umbral y detectar lineas

        trafficSignal(frame)

        mostrar_video(frame,maskBlue)
def enviar_datos(cx,hx):

    global tarea

    if tarea_auto_var.get() == 0:
        tarea = 3
    elif tarea_auto_var.get() == 1:     # Protocolo de presentación
        tarea = 1
        tarea_auto_var.set(0)
    elif tarea_auto_var.get() == 2:     # Protocolo de inciar viaje
        tarea = 2
    elif tarea_auto_var.get() == 3:     # Apagar el auto
        tarea = 3
    elif tarea_auto_var.get() == 4:     # Continuar
        tarea = 2

    data = f"{cx} {hx} {tarea}\n"

    #esp32.write(data.encode())
    print(cx,hx,tarea)
def RangoHSV(int):
    Hmin.set(sliderHmin.get())
    Hmax.set(sliderHmax.get())
    Smin.set(sliderSmin.get())
    Smax.set(sliderSmax.get())
    Vmin.set(sliderVmin.get())
    Vmax.set(sliderVmax.get())
def start_capture():

    # Iniciar la captura y muestra de pantalla en una nueva hebra
    t = threading.Thread(target=principal)
    t.daemon = True
    t.start()

    # Iniciar la función de pedir_cosas en otro hilo
    t_pedir_cosas = threading.Thread(target=pedir_cosas)
    t_pedir_cosas.daemon = True
    t_pedir_cosas.start()
def start_sending_data(cx, hx):

    # Iniciar el envío de datos a Arduino en un hilo separado
    t = threading.Thread(target=enviar_datos, args=(cx, hx))
    t.daemon = True
    t.start()

# Variables para los datos que enviarás a Arduino (ajusta según tus necesidades)

cx,hx = 0,0

tarea_auto_var = IntVar()
tarea_auto_var.set(3)

objetos_var = IntVar()
objetos_var.set(0)

kernel = np.ones((5,5),np.uint8)

minArea = 500  # Area minima para considerar que es un objeto


# Rango del 1er color

Hmin = IntVar()
Hmax = IntVar()
Smin = IntVar()
Smax = IntVar()
Vmin = IntVar()
Vmax = IntVar()

sliderHmin = Scale(panel_configuracion,label = 'Hmin', from_=0, to=255, orient=HORIZONTAL,command=RangoHSV,length=150,
                bg="gray10",fg='gainsboro',font=("Franklin Gothic Demi", 10))
sliderHmin.grid(row=0,column=0,padx=5,pady=5)
sliderHmin.set(0)

sliderSmin = Scale(panel_configuracion,label = 'Smin', from_=0, to=255, orient=HORIZONTAL,command=RangoHSV,length=150,
                bg="gray10",fg='gainsboro',font=("Franklin Gothic Demi", 10))
sliderSmin.grid(row=0,column=1,padx=5,pady=5)
sliderSmin.set(106)

sliderVmin = Scale(panel_configuracion,label = 'Vmin', from_=0, to=255, orient=HORIZONTAL,command=RangoHSV,length=150,
                bg="gray10",fg='gainsboro',font=("Franklin Gothic Demi", 10))
sliderVmin.grid(row=0,column=2,padx=5,pady=5)
sliderVmin.set(145)

sliderHmax = Scale(panel_configuracion,label = 'Hmax', from_=0, to=255, orient=HORIZONTAL,command=RangoHSV,length=150,
                bg="gray10",fg='gainsboro',font=("Franklin Gothic Demi", 10))
sliderHmax.grid(row=1,column=0,padx=5,pady=5)
sliderHmax.set(110)

sliderSmax = Scale(panel_configuracion,label = 'Smax', from_=0, to=255, orient=HORIZONTAL,command=RangoHSV,length=150,
                bg="gray10",fg='gainsboro',font=("Franklin Gothic Demi", 10))
sliderSmax.grid(row=1,column=1,padx=5,pady=5)
sliderSmax.set(171)

sliderVmax = Scale(panel_configuracion,label = 'Vmax', from_=0, to=255, orient=HORIZONTAL,command=RangoHSV,length=150,
                bg="gray10",fg='gainsboro',font=("Franklin Gothic Demi", 10))
sliderVmax.grid(row=1,column=2,padx=5,pady=5)
sliderVmax.set(255)

# Video en vivo del auto

video = Label(panel_camara,bg="snow")
video.grid(row=0)

video_umbral=Label(panel_objetos,bg="snow",bd=2)
video_umbral.grid(row=0,column=0)

# Iniciar captura y mostrar pantalla

start_capture()
start_sending_data(cx,hx)

def para_control():
    # En esta función se realizara un el cambio de control por internet a un cambio mas local que no requiera
    pass

ventana.mainloop()
