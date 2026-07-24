import customtkinter as ctk
import random
from tkinter import messagebox
from PIL import Image, ImageTk

ctk.set_appearance_mode("Light")  # PONER PARA QUE SE ADAPTE AL SISTEMA

class MemoramaEsteticoApp(ctk.CTkToplevel):

    def __init__(self, master=None):
        super().__init__(master)
        
        self.title("Microdescanso 2: Memorama")
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color="#C7D3EF") # COLOR AZUL DEL FONDO DE LA PANTALLA DE SOFTRELIEF
        
        ##PARA QUE ESTE FUNCIONA NECESITA LA IMAGEN HAY QUE CORREGIR ESTO PARA AYER
        # LOS OBJETOS QUE VAN APARECER EN EL LAS CARTAS.

        self.emojis_base = ['🏞️', '🐟', '🐍', '🪼', '🌌', '💧', '🪷', '🐊']
        self.emojis = []
        self.botones = []
        
        self.primera_carta = None
        self.segunda_carta = None
        self.pares_encontrados = 0
        self.puede_hacer_click = True
        
        # COLORES HAY QUE CAMBIAR LOS COLORES DEPENDE DE LA IMAGEN DE SOFTRELIEF
        self.color_carta_oculta = "#A26FD8"  
        self.color_carta_hover = "#C4A8F3"    
        self.color_carta_volteada = "#AAD9E5" 
        self.color_carta_par = "#F59E0B"        ##CAMNIAR LOS COLRES PARA QUE SE VES MAS MAGICOOO JAJAJAJ
        
        self.crear_interfaz()
        self.iniciar_juego()

    def crear_interfaz(self):
        ##FONDO DEL JUEGO PARA QWUE SE VEA LA IMAGEN
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(pady=30, padx=20, expand=True, fill="both")

        # TITULO DEL JUEGO :D!!!
        self.lbl_titulo = ctk.CTkLabel(self.main_frame, text="Memorama ", 
                                       font=ctk.CTkFont(size=28, weight="bold"), 
                                       text_color="white")
        self.lbl_titulo.pack(pady=10)
        
        # NO SE VA VER LA CUADRICULA YA QUE VA SER TRANSPARENTE
        self.grid_frame = ctk.CTkFrame(self.main_frame, fg_color=("#ffffff", "gray20"), corner_radius=20, bg_color="transparent")
        self.grid_frame.pack(pady=20, padx=20)
        
        # BOTONES PARA LAS CARTAS 4X4
        for i in range(4):
            self.grid_frame.grid_rowconfigure(i, weight=1)
            self.grid_frame.grid_columnconfigure(i, weight=1)
            
            for j in range(4):
                idx = i * 4 + j
                btn = ctk.CTkButton(
                    self.grid_frame, 
                    text="❔", 
                    font=ctk.CTkFont(size=45),
                    width=90, 
                    height=90,
                    corner_radius=15,
                    fg_color=self.color_carta_oculta,
                    hover_color=self.color_carta_hover,
                    text_color="white",
                    command=lambda i=idx: self.voltear_carta(i)
                )
                btn.grid(row=i, column=j, padx=12, pady=12)
                self.botones.append(btn)
                
        # ESTE ES EL APARTADO DONDE ESDTA EL BOTON PARA PODER REINICIAR EL JUEGO
        self.btn_reiniciar = ctk.CTkButton(self.main_frame, text="Volver a Jugar", 
                                           fg_color="#8ea2ff", hover_color="#7088ff", 
                                           corner_radius=20, font=ctk.CTkFont(weight="bold"),
                                           command=self.iniciar_juego)
        self.btn_reiniciar.pack(pady=15)

    def iniciar_juego(self):
        self.emojis = self.emojis_base * 2
        random.shuffle(self.emojis)
        
        self.primera_carta = None
        self.segunda_carta = None
        self.pares_encontrados = 0
        self.puede_hacer_click = True
        
        for btn in self.botones:
            btn.configure(text="❔", state="normal", fg_color=self.color_carta_oculta)

    def voltear_carta(self, indice):
        if not self.puede_hacer_click or self.botones[indice].cget("text") != "❔":
            return
            
        self.botones[indice].configure(text=self.emojis[indice], fg_color=self.color_carta_volteada)
        
        if self.primera_carta is None:
            self.primera_carta = indice
        else:
            self.segunda_carta = indice
            self.puede_hacer_click = False 
            self.verificar_par()

    def verificar_par(self):
        idx1 = self.primera_carta
        idx2 = self.segunda_carta
        
        if self.emojis[idx1] == self.emojis[idx2]:
            self.botones[idx1].configure(state="disabled", fg_color=self.color_carta_par) 
            self.botones[idx2].configure(state="disabled", fg_color=self.color_carta_par)
            self.pares_encontrados += 1
            self.reiniciar_turno()
            
            if self.pares_encontrados == 8:
                messagebox.showinfo("¡Has encontrado todos los pares!, Felicidades !")
        else:
            self.after(800, self.ocultar_cartas, idx1, idx2)

    def ocultar_cartas(self, idx1, idx2):
        self.botones[idx1].configure(text="❔", fg_color=self.color_carta_oculta)
        self.botones[idx2].configure(text="❔", fg_color=self.color_carta_oculta)
        self.reiniciar_turno()

    def reiniciar_turno(self):
        self.primera_carta = None
        self.segunda_carta = None
        self.puede_hacer_click = True

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()

    app = MemoramaEsteticoApp(master=root)
    app.protocol("WM_DELETE_WINDOW", root.destroy)

    root.mainloop()