"""
Este es el módulo principal de la interfaz gráfica del asistente virtual.
Desde aquí se controla la interfaz gráfica y se llama a los módulos de voz y a la función brain encargada de procesar la lógica.
"""
import tkinter as tk
from tkinter import PhotoImage
from tkinter import ttk

import threading


class AsistenteVirtualUI:
    def __init__(self, master):
        """
        Inicializa la clase y configura la ventana principal.

        Parámetros:
        - master: El objeto maestro que representa la ventana principal, en este caso, la variable root, de tipo Tk.
        """
        self.master = master
        # Funciones para la configuración inicial
        self.configurar_ventana()
        self.cargar_recursos()
        self.crear_widgets()
        self.stm = [""]*10
        # Creación del hilo (proceso paralelo) para la detección de la palabra clave
        hiloKeyword = threading.Thread(target=self.keyword_detected)
        hiloKeyword.daemon = True
        hiloKeyword.start()

    def configurar_ventana(self):
        """
        Configura la ventana principal de la aplicación.

        Esta función establece el título de la ventana, el color de fondo,
        las dimensiones y la capacidad de redimensionamiento de la ventana.
        """
        # Obtener la resolución de la pantalla
        ancho_pantalla = self.master.winfo_screenwidth()
        alto_pantalla = self.master.winfo_screenheight()

        # Ajustar estas variables según sea necesario
        ancho_ventana = 400
        altura_ventana = alto_pantalla -200 # La ventana ocupará todo el espacio vertical
        posicion_derecha = (ancho_pantalla-ancho_ventana)
        posicion_abajo = 0  # Centrar verticalmente

        # Establecer la geometría de la ventana
        self.master.geometry(f"{ancho_ventana}x{altura_ventana}+{posicion_derecha}+{posicion_abajo}")

        self.master.title("AVZaid")
        self.master.configure(bg='#2C2C2C')
        # Impide que la ventana se pueda redimensionar
        self.master.resizable(False, False)

    def cargar_recursos(self):
        """
        Carga los recursos necesarios para la aplicación.

        Esta función carga los iconos y las imágenes que se utilizarán en la interfaz gráfica.
        """
        # Icono del micrófono
        ruta_icono_microfono = "resources/images/microfono.png"
        self.icono_microfono = PhotoImage(file=ruta_icono_microfono)
        self.icono_microfono = self.icono_microfono.subsample(5, 5)
        self.icono_microfono_peque = self.icono_microfono.subsample(2, 2)
        # Flechas de la scrollbar
        self.up_arrow_image = PhotoImage(
            file='resources/images/uparrow 40.png').subsample(3, 3)
        self.down_arrow_image = PhotoImage(
            file='resources/images/downarrow 40.png').subsample(3, 3)
        self.up_arrow_pressed_image = PhotoImage(
            file='resources/images/uparrow 40.png').subsample(2, 2)
        self.down_arrow_pressed_image = PhotoImage(
            file='resources/images/downarrow 40.png').subsample(2, 2)

    def crear_widgets(self):
        """
        Crea y configura los widgets necesarios para la interfaz gráfica.

        Esta función crea y configura los siguientes widgets:
        - Botón de Añadir voz
        - Botón de escucha con ícono de micrófono redondo
        - Barra de texto para ingresar instrucciones
        - Botón para enviar la instrucción escrita
        - Frame, Canvas y Scrollbar para la sección de desplazamiento
        """
        # Botón de Añadir voz
        self.boton_anadir_voz = tk.Button(self.master, text="Añadir voz", command=self.abrir_ventana_anadir_voz, bg='#666666', fg='#FFFFFF', font=(
            'Helvetica', 10, 'bold'), borderwidth=1, relief="flat", activebackground='#525252', activeforeground='#FFFFFF')
        self.boton_anadir_voz.place(x=300, y=20)
        # Botón de escucha con ícono de micrófono redondo
        self.boton_escucha = tk.Button(self.master, image=self.icono_microfono,
                                       command=self.activar_escucha, bg='#2C2C2C', bd=0, highlightthickness=0, activebackground='#2C2C2C', height=200, width=200)
        self.boton_escucha.image = self.icono_microfono
        self.boton_escucha.pack(pady=150)
        # Botón para enviar la instrucción escrita
        self.boton_enviar = tk.Button(self.master, text="Enviar", command=self.enviar_instruccion, bg='#666666', fg='#FFFFFF', font=(
            'Helvetica', 16, 'bold'), borderwidth=1, relief="flat", activebackground='#525252', activeforeground='#FFFFFF')
        self.boton_enviar.pack(pady=10, side=tk.BOTTOM)
        # Barra de texto para ingresar instrucciones
        self.entry_texto = tk.Text(self.master, bg='#4C4C4C', fg='#FFFFFF',
                                   insertbackground='#FFFFFF', borderwidth=1, relief="flat", font=('Helvetica', 12), height=6)
        self.entry_texto.pack(fill='x', padx=20, pady=10, side=tk.BOTTOM)
        # Frame para la sección de desplazamiento
        # ---------------------------------------------------------------------
        # Creación de un estilo personalizado de la scrollbar
        self.style = ttk.Style()
        self.style.element_create(
            'Fruitsalad.Vertical.Scrollbar.trough', 'from', 'default')
        self.style.element_create(
            'Fruitsalad.Vertical.Scrollbar.thumb', 'from', 'default')
        self.style.element_create(
            'Fruitsalad.Vertical.Scrollbar.uparrow', 'from', 'default')
        self.style.element_create(
            'Fruitsalad.Vertical.Scrollbar.downarrow', 'from', 'default')
        self.style.element_create(
            'Fruitsalad.Vertical.Scrollbar.grip', 'from', 'default')
        # Configuración de las imágenes de las flechas de la scrollbar
        self.style.element_create('Custom.uparrow', 'image', self.up_arrow_image,
                                  ('pressed', self.up_arrow_pressed_image), border=15, sticky='')
        self.style.element_create('Custom.downarrow', 'image', self.down_arrow_image,
                                  ('pressed', self.down_arrow_pressed_image), border=15, sticky='')
        # Configuración del estilo de la scrollbar
        self.style.layout('Fruitsalad.Vertical.TScrollbar',
                          [
                              ('Fruitsalad.Vertical.Scrollbar.trough', {'children':
                                                                        [('Custom.uparrow', {'side': 'top', 'sticky': ''}),
                                                                         ('Custom.downarrow',
                                                                            {'side': 'bottom', 'sticky': ''}),
                                                                            ('Fruitsalad.Vertical.Scrollbar.thumb', {'unit': '1', 'children':
                                                                                                                     [('Fruitsalad.Vertical.Scrollbar.grip', {
                                                                                                                         'sticky': ''})],
                                                                                                                     'sticky': 'nswe'})],
                                                                        'sticky': 'ns'}),
                          ])
        self.style.configure('Fruitsalad.Vertical.TScrollbar',
                             troughcolor='#2C2C2C',
                             background='#4d4d4d',
                             arrowcolor='#8f8f8f',
                             borderwidth=0,
                             arrowborderwidth=0)
        self.style.map('Fruitsalad.Vertical.TScrollbar',
                       background=[('pressed', '!disabled', '#3d3d3d'),
                                   ('active', '#454545')])
        # Agregar el frame
        self.frame_scroll = tk.Frame(self.master, bg='#2C2C2C')
        self.frame_scroll.pack(fill='both', expand=True)
        # Canvas y Scrollbar
        self.canvas = tk.Canvas(
            self.frame_scroll, bg='#2C2C2C', bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.frame_scroll, orient="vertical", command=self.canvas.yview, style='Fruitsalad.Vertical.TScrollbar')
        self.frame_etiquetas = tk.Frame(self.canvas, bg='#2C2C2C')
        # Configuración de la scrollbar
        self.frame_etiquetas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        # Configuración del canvas
        self.canvas.create_window(
            (0, 0), window=self.frame_etiquetas, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        # ---------------------------------------------------------------------



    def activar_escucha(self):
        """
        Inicia un hilo para escuchar y actualizar.

        Esta función crea un hilo que ejecuta el método 'escuchar_y_actualizar'
        en segundo plano. El hilo se configura como un demonio para que se
        detenga automáticamente cuando el programa principal finalice.
        """
        hilo = threading.Thread(
            target=self.escuchar_y_actualizar)
        hilo.daemon = True
        hilo.start()

 
    def actualizar_texto(self, texto: str):
        """
        Actualiza el texto en el widget de entrada de texto.

        Parámetros:
        - texto (str): El texto que se desea insertar en el widget de entrada de texto.
        """
        self.entry_texto.delete(1.0, tk.END)
        self.entry_texto.insert(tk.END, texto)

    def agregar_etiqueta(self, texto: str, respuesta_asistente=False):
        """
        Agrega una etiqueta al marco de chat con el texto proporcionado.

        Parámetros:
        - texto (str): El texto que se mostrará en la etiqueta.
        - respuesta_asistente (bool, opcional): Indica si la etiqueta es una respuesta del asistente o no.
                                     Por defecto es False.
        """
        if respuesta_asistente:  # Si la etiqueta es una respuesta del asistente
            texto = "Zaid:\n\n" + texto
            estilo_label = {'bg': '#4C4C4C', 'fg': '#FFFFFF'}
        else:  # Si la etiqueta es una instrucción del usuario
            texto = "Yo:\n\n" + texto
            estilo_label = {'bg': '#4C4C4C', 'fg': '#FFFFFF'}
        # Crear la etiqueta
        label = tk.Label(self.frame_etiquetas, text=texto, **estilo_label,
                         width=50, wraplength=300, anchor='w', justify='left')
        label.pack(fill='x', padx=10, pady=5, expand=True)

    def enviar_instruccion(self):
        """
        Esta función se encarga de enviar una instrucción al asistente.
        Obtiene la instrucción ingresada por el usuario desde un widget de entrada de texto.
        Si la instrucción está vacía, la función retorna sin hacer nada.
        Agrega la etiqueta de la instrucción ingresada al GUI.
        Llama a la función 'brain' del módulo 'skills' para obtener la respuesta del asistente.
        Agrega la etiqueta de la respuesta del asistente al GUI.
        Borra el contenido del widget de entrada de texto.
        Y en caso de ser el primer mensaje: Configura la imagen del botón de escucha del asistente
        y empaqueta el botón de escucha y la barra de desplazamiento en el GUI.
        """
        # Obtener la instrucción ingresada por el usuario
        instruccion = self.entry_texto.get(1.0, tk.END).strip()
        if instruccion == "":
            return
        self.agregar_etiqueta(instruccion)
        # Mandar la instrucción al módulo de lógica y obtener la respuesta
        # Borrar el contenido del widget de entrada de texto
        self.entry_texto.delete(1.0, tk.END)
        # Configurar la imagen del botón de escucha del asistente
        self.boton_escucha.configure(image=self.icono_microfono_peque)
        self.boton_escucha.pack(pady=10)
        self.scrollbar.pack(side="right", fill="y")

    def confirmar_voz(self):
        """
        Confirma la voz seleccionada por el usuario.

        Esta función obtiene el nombre de la voz seleccionada por el usuario,
        cierra la ventana de añadir voz, actualiza el texto con el nombre de la voz
        seleccionada y envía la instrucción correspondiente.
        """
        nombre_voz = self.entrada_nombre_voz.get()
        self.ventana_anadir_voz.destroy()
        self.actualizar_texto(f"Clona mi voz, utiliza el nombre: {nombre_voz}")
        self.enviar_instruccion()

    def abrir_ventana_anadir_voz(self):
        """
        Abre una ventana para pedir el nombre de la voz al usuario.

        Esta función crea una nueva ventana utilizando la biblioteca Tkinter.
        La ventana muestra una etiqueta con instrucciones para ingresar el nombre de la voz,
        un campo de texto para ingresar el nombre y un botón para confirmar el ingreso.
        """
        self.ventana_anadir_voz = tk.Toplevel(self.master)
        self.ventana_anadir_voz.title("Añadir Voz")
        self.ventana_anadir_voz.geometry('300x150')
        self.ventana_anadir_voz.resizable(False, False)
        self.ventana_anadir_voz.configure(bg='#2C2C2C')
        # Etiqueta (label) con instrucciones
        etiqueta = tk.Label(self.ventana_anadir_voz, text="Ingrese el nombre de la voz",
                            bg='#2C2C2C', fg='#FFFFFF', font=('Helvetica', 12, 'bold'))
        etiqueta.pack(pady=(10, 0))  # Ajuste de espacio superior e inferior
        # Campo de texto para ingresar el nombre
        self.entrada_nombre_voz = tk.Entry(
            self.ventana_anadir_voz, bg='#4C4C4C', fg='#FFFFFF')
        self.entrada_nombre_voz.pack(pady=10)
        # Botón para confirmar el ingreso
        boton_confirmar = tk.Button(
            self.ventana_anadir_voz, text="Confirmar", command=self.confirmar_voz)
        boton_confirmar.pack()


def main():
    """
    Función principal del programa.
    Inicializa la ventana principal y ejecuta el bucle principal del programa.
    """
    def check_minimized():
        if root.state() == 'iconic':  # Si la ventana está minimizada
            hide_window()
        # Revisar nuevamente después de 100 ms
        root.after(100, check_minimized)

    def hide_window():
        root.withdraw()  # Oculta la ventana

    root = tk.Tk()
    app = AsistenteVirtualUI(root)
    root.after(100, check_minimized)
    root.mainloop()


if __name__ == "__main__":
    """
    Esta condición se cumple cuando el archivo se ejecuta directamente.
    Es solo una buena práctica, es lo mismo que solo poner 'main()'.
    """
    main()

