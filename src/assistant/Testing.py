import tkinter as tk
from tkinter import ttk

class MiVentana:
    def __init__(self, master):
        self.master = master
        master.title("Ejemplo Tkinter")

        # Imagen centrada horizontalmente
        self.imagen = tk.PhotoImage(file="resources/images/microfono.png")  # Reemplaza "ruta_de_tu_imagen.png" con la ruta correcta
        self.label_imagen = tk.Label(master, image=self.imagen)
        self.label_imagen.pack(pady=10)

        # Botón debajo de la imagen
        self.boton = tk.Button(master, text="Botón debajo de la imagen", command=self.funcion_boton)
        self.boton.pack(pady=10)

        # Frame centrado horizontalmente
        self.frame = tk.Frame(master)
        self.frame.pack(pady=10)

        # Entry de texto a la izquierda
        self.entry_texto = tk.Entry(self.frame)
        self.entry_texto.pack(side=tk.LEFT, padx=5)

        # Botón de enviar a la derecha
        self.boton_enviar = tk.Button(self.frame, text="Enviar", command=self.funcion_enviar)
        self.boton_enviar.pack(side=tk.RIGHT, padx=5)

    def funcion_boton(self):
        # Lógica del botón
        print("¡Botón presionado!")

    def funcion_enviar(self):
        # Lógica del botón enviar
        texto = self.entry_texto.get()
        print(f"Texto enviado: {texto}")

if __name__ == "__main__":
    root = tk.Tk()
    ventana = MiVentana(root)
    root.mainloop()