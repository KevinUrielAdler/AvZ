import tkinter as tk
from tkinter import PhotoImage
from tkinter import ttk

import assistant.voice as voice
import threading

import assistant.skills as skills


class AsistenteVirtualUI:
    def __init__(self, master):
        self.master = master
        self.configurar_ventana()
        self.cargar_recursos()
        self.crear_widgets()
        self.stm = [""]*10

        hiloKeyword = threading.Thread(target=self.keyword_detected)
        hiloKeyword.daemon = True
        hiloKeyword.start()

    def keyword_detected(self):
        while True:
            if voice.keyword_function_mic():
                self.master.deiconify()
                self.master.after(0, self.activar_escucha)

    def configurar_ventana(self):
        self.master.title("AVZaid")
        self.master.configure(bg='#2C2C2C')
        self.master.geometry('400x700')
        self.master.resizable(False, False)

    def cargar_recursos(self):
        # Asegúrate de que esta imagen tenga un fondo redondo
        ruta_icono_microfono = "resources/images/microfono.png"
        self.icono_microfono = PhotoImage(file=ruta_icono_microfono)
        # Cambia el tamaño de la imagen
        self.icono_microfono = self.icono_microfono.subsample(5, 5)
        self.icono_microfono_peque = self.icono_microfono.subsample(2, 2)

    def crear_widgets(self):
        # Botón de Añadir voz
        self.boton_anadir_voz = tk.Button(self.master, text="Añadir voz", command=self.abrir_ventana_anadir_voz, bg='#666666', fg='#FFFFFF', font=(
            'Helvetica', 10, 'bold'), borderwidth=1, relief="flat", activebackground='#525252', activeforeground='#FFFFFF')
        # Ajusta la posición según necesites
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
        # Estilo de la scrollbar
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

        self.up_arrow_image = PhotoImage(
            file='resources/images/uparrow 40.png').subsample(3, 3)
        self.down_arrow_image = PhotoImage(
            file='resources/images/downarrow 40.png').subsample(3, 3)
        self.up_arrow_pressed_image = PhotoImage(
            file='resources/images/uparrow 40.png').subsample(2, 2)
        self.down_arrow_pressed_image = PhotoImage(
            file='resources/images/downarrow 40.png').subsample(2, 2)
        self.style.element_create('Custom.uparrow', 'image', self.up_arrow_image,
                                  ('pressed', self.up_arrow_pressed_image), border=15, sticky='')
        self.style.element_create('Custom.downarrow', 'image', self.down_arrow_image,
                                  ('pressed', self.down_arrow_pressed_image), border=15, sticky='')

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

        self.frame_scroll = tk.Frame(self.master, bg='#2C2C2C')
        self.frame_scroll.pack(fill='both', expand=True)

        # Canvas y Scrollbar
        self.canvas = tk.Canvas(
            self.frame_scroll, bg='#2C2C2C', bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self.frame_scroll, orient="vertical", command=self.canvas.yview, style='Fruitsalad.Vertical.TScrollbar')
        self.frame_etiquetas = tk.Frame(self.canvas, bg='#2C2C2C')

        self.frame_etiquetas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0), window=self.frame_etiquetas, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        # ---------------------------------------------------------------------

    def activar_escucha(self):
        print("Escuchando...")
        hilo = threading.Thread(
            target=self.escuchar_y_actualizar)
        hilo.daemon = True
        hilo.start()

    def escuchar_y_actualizar(self):
        texto = voice.speech_recognize_once_from_mic()
        self.master.after(0, self.actualizar_texto, texto)
        self.master.after(0, self.enviar_instruccion)

    def actualizar_texto(self, texto):
        self.entry_texto.delete(1.0, tk.END)
        self.entry_texto.insert(tk.END, texto)

    def agregar_etiqueta(self, texto, respuesta_asistente=False):
        if respuesta_asistente:
            texto = "Zaid:\n\n" + texto
            estilo_label = {'bg': '#4C4C4C', 'fg': '#FFFFFF'}
        else:
            texto = "Yo:\n\n" + texto
            estilo_label = {'bg': '#4C4C4C', 'fg': '#FFFFFF'}

        label = tk.Label(self.frame_etiquetas, text=texto, **estilo_label,
                         width=50, wraplength=300, anchor='w', justify='left')
        label.pack(fill='x', padx=10, pady=5, expand=True)

    def enviar_instruccion(self):
        instruccion = self.entry_texto.get(1.0, tk.END).strip()
        if instruccion == "":
            return
        self.agregar_etiqueta(instruccion)
        respuesta_asistente = skills.brain(instruccion, self.stm)
        self.agregar_etiqueta(respuesta_asistente,
                              respuesta_asistente=True)
        self.entry_texto.delete(1.0, tk.END)
        self.boton_escucha.configure(image=self.icono_microfono_peque)
        self.boton_escucha.pack(pady=10)
        self.scrollbar.pack(side="right", fill="y")

    def confirmar_voz(self):
        nombre_voz = self.entrada_nombre_voz.get()
        self.ventana_anadir_voz.destroy()
        self.actualizar_texto(f"Clona mi voz, utiliza el nombre: {nombre_voz}")
        self.enviar_instruccion()

    def abrir_ventana_anadir_voz(self):
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
    main()
