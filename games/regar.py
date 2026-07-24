import customtkinter as ctk
import tkinter as tk
import math
import random

class RefugioEstudiantil(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- CONFIGURACIÓN DE VENTANA ---
        self.title("SoftRelief - Refugio de Cristal")
        self.geometry("1000x750")
        self.configure(fg_color="#E8E4F2") 

        # --- ESTADO DE RIEGO POR ETAPAS ---
        self.etapa_riego = 0        
        self.escala_nenufar = 0.0   
        self.escala_flor = 0.0      
        self.frame_agua = 0         
        self.frame_flote = 0        
        self.frase_actual = ""

        self.frases_bienestar = [
            "Respira.",
            "No tienes que resolver toda tu vida hoy, solo da el siguiente paso..",
            "Las tormentas no duran para siempre.",
            "Despeja la mente. Las buenas ideas llegan en la calma.",
            "Avanzar lento sigue siendo avanzar.",
            "Tu bienestar vale mas que cualquier pendiente."
        ]

        # 5 Lotos de diferentes tamaños: (X, Y, Escala, Desfase)
        self.datos_lotos = [
            (250, 380, 0.50, 0),   # Pequeñita izquierda
            (380, 420, 0.90, 15),  # Mediana
            (500, 450, 1.40, 30),  # Gigante central
            (640, 410, 0.75, 45),  # Normal derecha
            (760, 380, 0.45, 60) # Mini fondo derecha
        ]

        # 4 Ranitas de diferentes tamaños: (X, Y, Escala, Desfase)
        self.datos_ranitas = [
            (150, 550, 0.7, 0),    # Ranita bebé izquierda
            (280, 610, 1.5, 20),   # Rana grandota izquierda
            (720, 590, 1.1, 40),   # Rana mediana derecha
            (860, 530, 0.5, 60)    # Ranita bebé fondo derecha
        ]

        # 45 Libélulas mágicas
        self.libelulas = []
        indice_libelula = 0
        while indice_libelula < 45: 
            x_ini = random.randint(20, 980)
            y_ini = random.randint(20, 730)
            vel = random.uniform(0.015, 0.04)
            tam = random.uniform(3, 5) 
            if indice_libelula % 2 == 0:
                color_halo, color_centro = "#FCF3CF", "#FFF700" 
            else:
                color_halo, color_centro = "#D0ECE7", "#00FFEA" 
            self.libelulas.append([x_ini, y_ini, vel, tam, color_halo, color_centro])
            indice_libelula += 1

        # --- INTERFAZ GRÁFICA ---
        self.frame_cabecera = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cabecera.pack(pady=(25, 10))

        self.titulo = ctk.CTkLabel(self.frame_cabecera, text="Respira y Florece", font=ctk.CTkFont(family="Helvetica", size=38, weight="bold"), text_color="#645877")
        self.titulo.pack()
        
        self.subtitulo = ctk.CTkLabel(self.frame_cabecera, text="Riega el estanque. Las ranitas te hacen compañía.", font=ctk.CTkFont(size=16), text_color="#8A9CA8")
        self.subtitulo.pack(pady=(5, 15))

        self.btn_accion = ctk.CTkButton(
            self.frame_cabecera, text="💧 Regar un poco", font=ctk.CTkFont(size=16, weight="bold"), 
            fg_color="#A9DFD6", text_color="#4B3B69", hover_color="#C7F0E5", 
            width=240, height=50, corner_radius=25, command=self.accionar_riego
        )
        self.btn_accion.pack()

        self.canvas = tk.Canvas(self, bg="#E8E4F2", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.bucle_flotacion()

    # --- MOTOR DE VIDA CONTINUA ---
    def bucle_flotacion(self):
        self.frame_flote += 1
        self.dibujar_escena()
        self.after(35, self.bucle_flotacion) 

    # --- LÓGICA DE RIEGO (If/Elif) ---
    def accionar_riego(self):
        self.btn_accion.configure(state="disabled")
        
        if self.etapa_riego < 3:
            self.frame_agua = 1
            self.animar_lluvia()
        elif self.etapa_riego == 3:
            self.etapa_riego = 0
            self.escala_nenufar = 0.0
            self.escala_flor = 0.0
            self.frase_actual = ""
            self.btn_accion.configure(text="💧 Regar un poco", state="normal")

    def animar_lluvia(self):
        if self.frame_agua < 40:
            self.frame_agua += 1
            self.after(20, self.animar_lluvia)
        else:
            self.frame_agua = 0
            
            if self.etapa_riego == 0:
                self.etapa_riego = 1
                self.animar_nenufares()
            elif self.etapa_riego == 1:
                self.etapa_riego = 2
                self.animar_capullos()
            elif self.etapa_riego == 2:
                self.etapa_riego = 3
                indice_random = random.randint(0, len(self.frases_bienestar) - 1)
                self.frase_actual = self.frases_bienestar[indice_random]
                self.animar_flores()

    def animar_nenufares(self):
        if self.escala_nenufar < 1.0:
            self.escala_nenufar += 0.05
            self.after(30, self.animar_nenufares)
        else:
            self.btn_accion.configure(state="normal")

    def animar_capullos(self):
        if self.escala_flor < 0.3:
            self.escala_flor += 0.02
            self.after(30, self.animar_capullos)
        else:
            self.btn_accion.configure(state="normal")

    def animar_flores(self):
        if self.escala_flor < 1.0:
            self.escala_flor += 0.02 
            self.after(30, self.animar_flores)
        else:
            self.btn_accion.configure(text="✨ Limpiar estanque", state="normal")

    # --- RENDERIZADO VISUAL ---
    def dibujar_escena(self):
        self.canvas.delete("all")
        
        # 1. Fondo cielo mágico
        self.dibujar_cielo()

        # 2. Estanque de cristal (Ocupa el centro-arriba)
        pulso = math.sin(self.frame_flote * 0.04) * 4
        cx, cy = 500, 400 
        radio_x, radio_y = 380, 130
        
        self.canvas.create_oval(cx - radio_x - pulso, cy - radio_y - pulso, cx + radio_x + pulso, cy + radio_y + pulso, outline="#FFFFFF", width=1)
        self.canvas.create_oval(cx - radio_x + 15, cy - radio_y + 10, cx + radio_x - 15, cy + radio_y - 10, fill="#D6EAF8", outline="#EAF4F7", width=2)
        self.canvas.create_oval(cx - radio_x + 30 + pulso, cy - radio_y + 20 + pulso, cx + radio_x - 30 - pulso, cy + radio_y - 20 - pulso, fill="#E6F7F9", outline="#D3EDEE", width=3)

        # 3. Orillas del estanque (Pasto mágico)
        self.dibujar_orillas()

        # 4. Iterar sobre las flores de diferentes tamaños (En el agua)
        indice_loto = 0
        while indice_loto < len(self.datos_lotos):
            x_base, y_base, escala_base, desfase = self.datos_lotos[indice_loto]
            
            movimiento_y = math.sin((self.frame_flote + desfase) * 0.06) * 5
            y_actual = y_base + movimiento_y
            
            escala_n_total = self.escala_nenufar * escala_base
            escala_f_total = self.escala_flor * escala_base

            # Nenúfar
            if escala_n_total > 0.01:
                self.dibujar_nenufar(x_base, y_actual, escala_n_total)

            # Lluvia y Ondas
            if self.frame_agua > 0:
                fase_gota = self.frame_agua - (indice_loto * 4)
                if 0 < fase_gota < 20:
                    y_gota = 150 + (fase_gota * 15)
                    self.canvas.create_oval(x_base - 2, y_gota, x_base + 2, y_gota + 15, fill="#FFFFFF", outline="")
                elif 20 <= fase_gota < 40:
                    radio_onda = (fase_gota - 20) * 4
                    self.canvas.create_oval(x_base - radio_onda, y_actual - (radio_onda * 0.3), x_base + radio_onda, y_actual + (radio_onda * 0.3), outline="#A9DFD6", width=2)

            # Capullos / Flores
            if escala_f_total > 0.01:
                self.dibujar_petalos(x_base, y_actual - (5 * escala_base), escala_f_total)

            indice_loto += 1

        # 5. Iterar sobre las Ranitas de diferentes tamaños (En la orilla)
        indice_ranita = 0
        while indice_ranita < len(self.datos_ranitas):
            x_rana, y_rana, escala_rana, desfase_rana = self.datos_ranitas[indice_ranita]
            
            if self.etapa_riego >= 1:
                # Modificamos la escala general por la escala propia de la rana
                self.dibujar_ranita(x_rana, y_rana, escala_rana * self.escala_nenufar, desfase_rana)
                
            indice_ranita += 1

        # 6. Libélulas flotando por TODA la pantalla
        if self.etapa_riego >= 1:
            i_lib = 0
            while i_lib < len(self.libelulas):
                x_ini, y_ini, vel, tam, color_halo, color_centro = self.libelulas[i_lib]
                
                dx = math.sin(self.frame_flote * vel + x_ini) * 40
                dy = math.cos(self.frame_flote * vel * 0.7 + y_ini) * 30
                
                x_actual = x_ini + dx
                y_actual = y_ini + dy
                
                self.canvas.create_oval(x_actual - tam*1.5, y_actual - tam*1.5, x_actual + tam*1.5, y_actual + tam*1.5, fill=color_halo, outline="")
                self.canvas.create_oval(x_actual - tam/2, y_actual - tam/2, x_actual + tam/2, y_actual + tam/2, fill=color_centro, outline="")
                
                i_lib += 1

        # 7. Frase Random
        if self.etapa_riego == 3:
            mov_texto = math.sin(self.frame_flote * 0.03) * 3
            self.canvas.create_text(
                500, 110 + mov_texto, 
                text=self.frase_actual, 
                font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), 
                fill="#8C7AAB", 
                justify="center"
            )

        self.canvas.create_text(500, 680, text="SoftRelief 🪷", font=("Helvetica", 18, "bold"), fill="#B8A9C9")

    def dibujar_cielo(self):
        ola1 = [0, 200, 500, 100, 1000, 250, 1000, 750, 0, 750]
        self.canvas.create_polygon(ola1, fill="#E3DEF0", outline="", smooth=True)

    def dibujar_orillas(self):
        pasto = [
            0, 500, 
            200, 520, 
            400, 560, 
            600, 550, 
            800, 510, 
            1000, 480, 
            1000, 750, 
            0, 750
        ]
        self.canvas.create_polygon(pasto, fill="#D1E8E2", outline="", smooth=True)
        
        borde_pasto = [0, 500, 200, 520, 400, 560, 600, 550, 800, 510, 1000, 480]
        self.canvas.create_line(borde_pasto, fill="#A9DFD6", width=4, smooth=True)

    def dibujar_ranita(self, x, y, escala, desfase):
        self.canvas.create_oval(x - 22*escala, y + 2*escala, x + 22*escala, y + 12*escala, fill="#C4DDD8", outline="")
        
        breathe = math.sin(self.frame_flote * 0.1 + desfase) * (2 * escala)
        
        self.canvas.create_oval(x - 18*escala, y - 15*escala - breathe, x + 18*escala, y + 8*escala, fill="#86EFAC", outline="#4ADE80", width=max(1, int(2*escala)))
        
        if (self.frame_flote + desfase) % 80 > 5:
            self.canvas.create_oval(x - 16*escala, y - 28*escala - breathe, x - 2*escala, y - 10*escala - breathe, fill="#FFFFFF", outline="#4ADE80", width=max(1, int(2*escala)))
            self.canvas.create_oval(x + 2*escala, y - 28*escala - breathe, x + 16*escala, y - 10*escala - breathe, fill="#FFFFFF", outline="#4ADE80", width=max(1, int(2*escala)))
            self.canvas.create_oval(x - 10*escala, y - 22*escala - breathe, x - 6*escala, y - 16*escala - breathe, fill="#1F2937")
            self.canvas.create_oval(x + 6*escala, y - 22*escala - breathe, x + 10*escala, y - 16*escala - breathe, fill="#1F2937")
        else:
            self.canvas.create_arc(x - 16*escala, y - 22*escala - breathe, x - 2*escala, y - 12*escala - breathe, start=0, extent=180, outline="#4ADE80", width=max(1, int(3*escala)), style=tk.ARC)
            self.canvas.create_arc(x + 2*escala, y - 22*escala - breathe, x + 16*escala, y - 12*escala - breathe, start=0, extent=180, outline="#4ADE80", width=max(1, int(3*escala)), style=tk.ARC)

    def dibujar_nenufar(self, x, y, escala):
        radio_x = 55 * escala
        radio_y = 22 * escala
        self.canvas.create_arc(
            x - radio_x, y - radio_y, x + radio_x, y + radio_y,
            start=40, extent=280, fill="#A7F3D0", outline="#FFFFFF", width=2, style=tk.PIESLICE
        )
        self.canvas.create_line(x, y, x - (25*escala), y + (10*escala), fill="#FFFFFF", width=1)
        self.canvas.create_line(x, y, x + (30*escala), y + (8*escala), fill="#FFFFFF", width=1)

    def dibujar_petalos(self, x, y, escala):
        petalos = [
            ("#BBA5F5", -75, -15, -70, -60, -35, -35), 
            ("#6EE7B7",  75, -15,  70, -60,  35, -35), 
            ("#C9B5F9", -55, -35, -40, -90, -15, -55), 
            ("#A7F3D0",  55, -35,  40, -90,  15, -55), 
            ("#FFFFFF", -30, -50,   0, -105,  30, -50)  
        ]

        indice_petalo = 0
        while indice_petalo < len(petalos):
            color, cx1, cy1, px, py, cx2, cy2 = petalos[indice_petalo]
            puntos = [
                x, y, 
                x + (cx1 * escala), y + (cy1 * escala),
                x + (px * escala), y + (py * escala), 
                x + (cx2 * escala), y + (cy2 * escala) 
            ]
            self.canvas.create_polygon(puntos, fill=color, outline="#FFFFFF", width=1, smooth=True)
            indice_petalo += 1

if __name__ == "__main__":
    app = RefugioEstudiantil()
    app.mainloop()