import tkinter as tk
from tkinter import PhotoImage

import assistant.voice as voice
import threading


class AsistenteVirtualUI:
    def __init__(self, master):
        self.master = master
        self.configurar_ventana()
        self.cargar_recursos()
        self.crear_widgets()

        hiloKeyword = threading.Thread(target=self.keyword_detected)
        hiloKeyword.daemon = True
        hiloKeyword.start()

    def keyword_detected(self):
        while True:
            if voice.keyword_function_mic():
                self.master.deiconify()
                self.master.after(0, self.activar_escucha)

    def configurar_ventana(self):
        self.master.title("Asistente Virtual Zaid")
        self.master.configure(bg='#2C2C2C')
        self.master.geometry('400x700')
        self.master.resizable(False, False)

    def cargar_recursos(self):
        # Asegúrate de que esta imagen tenga un fondo redondo
        ruta_icono_microfono = "resources/images/microfono.png"
        self.icono_microfono = PhotoImage(file=ruta_icono_microfono)
        # Cambia el tamaño de la imagen
        self.icono_microfono = self.icono_microfono.subsample(5, 5)

    def crear_widgets(self):
        # Botón de escucha con ícono de micrófono redondo
        self.boton_escucha = tk.Button(self.master, image=self.icono_microfono,
                                       command=self.activar_escucha, bg='#2C2C2C', bd=0, highlightthickness=0, activebackground='#2C2C2C', height=200, width=200)
        self.boton_escucha.image = self.icono_microfono
        self.boton_escucha.pack(pady=150)

        # Botón para enviar la instrucción escrita
        self.boton_enviar = tk.Button(self.master, text="Enviar", command=self.enviar_instruccion,
                                      bg='#666666', fg='#FFFFFF', font=('Helvetica', 16, 'bold'), borderwidth=1, relief="flat")
        self.boton_enviar.pack(pady=10, side=tk.BOTTOM)

        # Barra de texto para ingresar instrucciones
        self.entry_texto = tk.Text(self.master, bg='#4C4C4C', fg='#FFFFFF',
                                   insertbackground='#FFFFFF', borderwidth=1, relief="flat", font=('Helvetica', 12), height=8)
        self.entry_texto.pack(fill='x', padx=20, pady=10, side=tk.BOTTOM)

    def activar_escucha(self):
        print("Escuchando...")
        hilo = threading.Thread(target=self.escuchar_y_actualizar)
        hilo.daemon = True
        hilo.start()

    def escuchar_y_actualizar(self):
        texto = voice.speech_recognize_once_from_mic()
        self.master.after(0, self.actualizar_texto, texto)

    def enviar_instruccion(self):
        instruccion = self.entry_texto.get(1.0, tk.END)
        print(f"Instrucción enviada: {instruccion}")
        self.entry_texto.delete(1.0, tk.END)

    def actualizar_texto(self, texto):
        self.entry_texto.delete(1.0, tk.END)
        self.entry_texto.insert(tk.END, texto)


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
