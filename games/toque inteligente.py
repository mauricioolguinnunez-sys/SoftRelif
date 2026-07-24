##AQUI EMPEZAMOS A RELIZAR EL JUEGO

import customtkinter as ctk
import tkinter as tk
import math
import random

class PaisajeBurbujasPastel(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        #CONFIGURACIÓN DE VENTANA, QUE TAMANO Y QUE VA DECIR 
        self.title("Microdescanso 1: Burbujas.")
        self.state("zoomed")
        
        # COLOR DEL FONDO DEL JUEGO
        self.color_cielo = "#D1EEEE" 
        self.configure(fg_color=self.color_cielo) 

        #  ESTADO DEL JUEGO 
        self.estado = "Inicio"      
        self.puntos = 0
        self.meta_puntos = 25
        self.tiempo_restante = 30   
        
        self.frame_flote = 0
        
        self.burbujas_flotantes = []     
        self.burbujas_desvaneciendo = [] 
        
        # METER A LAS LIBELULAS
        self.libelulas = []
        indice_libelula = 0
        while indice_libelula < 35: 
            x_ini = random.randint(20, 980)
            y_ini = random.randint(200, 730)
            vel = random.uniform(0.005, 0.015) 
            tam = random.uniform(2, 4) 
            if indice_libelula % 2 == 0:
                self.libelulas.append([x_ini, y_ini, vel, tam, "#FFF9C4", "#FFF59D"]) 
            else:
                self.libelulas.append([x_ini, y_ini, vel, tam, "#E0F7FA", "#B2EBF2"]) 
            indice_libelula += 1

        #RANAS DEL FONDO, LOTOS
        self.lotos_fondo = [
            (250, 480, 0.8, 0),
            (480, 520, 1.2, 15),
            (720, 470, 0.7, 30),
            (880, 560, 0.9, 45)
        ]
        
        self.ranitas_fondo = [
            (150, 600, 1.4, 10),  # Rana en la orilla izquierda
            (480, 515, 0.8, 15),  # Ranita sobre el loto central
            (820, 480, 0.6, 50)   # Ranita pequena a lo lejos
        ]

        # ESTE ES LA INTERFAZ GRAFICA, LO QUE VA VER EL USUARIO
        self.frame_cabecera = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cabecera.pack(pady=(15, 5))

        self.titulo = ctk.CTkLabel(self.frame_cabecera, text="Reto de Cristal", font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"), text_color="#897C9E")
        self.titulo.pack()
        
        self.subtitulo = ctk.CTkLabel(self.frame_cabecera, text="Revienta 25 burbujas antes de que lleguen al cielo.", font=ctk.CTkFont(size=16), text_color="#A39BB0")
        self.subtitulo.pack(pady=(0, 5))

        self.btn_accion = ctk.CTkButton(
            self.frame_cabecera, text="▶ Comenzar Reto", font=ctk.CTkFont(size=15, weight="bold"), 
            fg_color="#A2DCE8", text_color="#526A7A", hover_color="#C0E8F0", 
            width=200, height=40, corner_radius=20, command=self.iniciar_juego
        )
        self.btn_accion.pack(pady=5)

        # COMO SE VA VER EL RESTO DE LA PANTALLA !!!!ARREGLAR!!!!!!, DEBE DE VERSE MAS NATURAL
        self.canvas = tk.Canvas(self, bg=self.color_cielo, highlightthickness=0, cursor="tcross")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.accion_clic)

        # INICIAR LA ANIMACION DE LAS BURBUJAS
        self.bucle_animacion()

    # AQUI SE DETERMINA EL TIEMPO DE CADA JUEGO
    def reloj_temporizador(self):
        if self.estado == "Jugando":
            if self.tiempo_restante > 0:
                self.tiempo_restante -= 1
                self.after(1000, self.reloj_temporizador)
            else:
                self.evaluar_resultado()

    def iniciar_juego(self):
        self.estado = "Jugando"
        self.puntos = 0
        self.tiempo_restante = 30
        self.burbujas_flotantes = []
        self.burbujas_desvaneciendo = []
        self.btn_accion.configure(state="disabled", text="Jugando...")
        self.subtitulo.configure(text="Libera el estrés. Concéntrate en las burbujas.")
        self.reloj_temporizador()

##CUENTA LAS PUNTOS QUE GANAS Y EN CASO DE QUE SE PIERDA EL JUEGO
    def evaluar_resultado(self):
        if self.puntos >= self.meta_puntos:
            self.estado = "Ganado"
            self.subtitulo.configure(text="¡Misión Cumplida! Disfruta la paz del paisaje.")
            self.burbujas_flotantes = [] 
        else:
            self.estado = "Perdido"
            self.subtitulo.configure(text="¡El tiempo se acabó! Tómate un respiro y vuelve a intentarlo.")
            
        self.btn_accion.configure(state="normal", text="↻ Reintentar")

    # AQUI LAS VIDAS
    def bucle_animacion(self):
        self.frame_flote += 1
        self.actualizar_logica()
        self.dibujar_escena()
        self.after(20, self.bucle_animacion) 

    # LOGICA DEL JUEGO
    def actualizar_logica(self):
        if self.estado == "Jugando":
            if random.randint(1, 100) <= 6: 
                x_ini = random.randint(50, 950)
                y_ini = 650
                radio = random.randint(25, 50)
                vel = random.uniform(1.0, 2.5) 
                osc = random.uniform(0.01, 0.02) 
                
                
                color_ran = random.randint(0, 3)
                if color_ran == 0:
                    color = "#8BADD9" 
                elif color_ran == 1:
                    color = "#D8D7F6"
                elif color_ran == 2:
                    color = "#EED5F2"
                elif color_ran == 3:
                    color = "#E1EBF7"
                    
                self.burbujas_flotantes.append([x_ini, y_ini, radio, vel, color, osc])

        # MOVER LAS BURBUJAS
        i = 0
        while i < len(self.burbujas_flotantes):
            self.burbujas_flotantes[i][1] -= self.burbujas_flotantes[i][3]
            if self.burbujas_flotantes[i][1] < -80:
                self.burbujas_flotantes.pop(i)
            else:
                i += 1

        # ANIMACION DE LAS BURBUJAS DESAPARECIENDO
        j = 0
        while j < len(self.burbujas_desvaneciendo):
            self.burbujas_desvaneciendo[j][2] += 1.5 
            self.burbujas_desvaneciendo[j][3] -= 1 
            
            if self.burbujas_desvaneciendo[j][3] <= 0:
                self.burbujas_desvaneciendo.pop(j)
            else:
                j += 1

    def accion_clic(self, evento):
        if self.estado == "Jugando":
            x_clic = evento.x
            y_clic = evento.y
            
            k = 0
            while k < len(self.burbujas_flotantes):
                x_burbuja = self.burbujas_flotantes[k][0]
                x_real = x_burbuja + math.sin(self.frame_flote * self.burbujas_flotantes[k][5]) * 40
                y_burbuja = self.burbujas_flotantes[k][1]
                radio = self.burbujas_flotantes[k][2]
                
                distancia = math.sqrt((x_clic - x_real)**2 + (y_clic - y_burbuja)**2)
                
                if distancia <= radio:
                    # Guardamos [x, y, radio_actual, vida_frames]
                    self.burbujas_desvaneciendo.append([x_real, y_burbuja, radio, 20]) 
                    self.burbujas_flotantes.pop(k)
                    self.puntos += 1
                    break 
                else:
                    k += 1

    # COMO SE VA AVER
    def dibujar_escena(self):
        self.canvas.delete("all")
        
        #EL FONDO
        self.dibujar_fondo_natural()

        # LOTOS EEN EL FONDO
        idx_loto = 0
        while idx_loto < len(self.lotos_fondo):
            x, y, escala, desfase = self.lotos_fondo[idx_loto]
            mov_y = math.sin(self.frame_flote * 0.03 + desfase) * 4
            self.dibujar_nenufar_y_loto(x, y + mov_y, escala)
            idx_loto += 1

        ##RANITAS DURMIENDO
        idx_rana = 0
        while idx_rana < len(self.ranitas_fondo):
            x_r, y_r, esc_r, des_r = self.ranitas_fondo[idx_rana]
            mov_y_rana = math.sin(self.frame_flote * 0.03 + des_r) * 4
            self.dibujar_ranita(x_r, y_r + mov_y_rana, esc_r, des_r)
            idx_rana += 1

        # LIBELULAS
        i_lib = 0
        while i_lib < len(self.libelulas):
            x_ini, y_ini, vel, tam, color_halo, color_centro = self.libelulas[i_lib]
            
            dx = math.sin(self.frame_flote * vel + x_ini) * 50
            dy = math.cos(self.frame_flote * vel * 0.7 + y_ini) * 30
            
            if self.estado == "Ganado":
                dx = math.sin(self.frame_flote * vel * 1.5 + x_ini) * 60
                dy = math.cos(self.frame_flote * vel * 1.2 + y_ini) * 50

            x_actual = x_ini + dx
            y_actual = y_ini + dy
            
            self.canvas.create_oval(x_actual - tam*1.5, y_actual - tam*1.5, x_actual + tam*1.5, y_actual + tam*1.5, fill=color_halo, outline="")
            self.canvas.create_oval(x_actual - tam/2, y_actual - tam/2, x_actual + tam/2, y_actual + tam/2, fill=color_centro, outline="")
            i_lib += 1

        color_tiempo = "#897C9E"
        if self.tiempo_restante <= 10:
            color_tiempo = "#F1948A" 

        texto_marcador = f"Puntos: {self.puntos} / {self.meta_puntos}"
        texto_reloj = f"⏳ {self.tiempo_restante}s"
        
        self.canvas.create_text(120, 20, text=texto_marcador, font=("Helvetica", 20, "bold"), fill="#897C9E")
        self.canvas.create_text(900, 20, text=texto_reloj, font=("Helvetica", 20, "bold"), fill=color_tiempo)

        # LAS BURBUJAS QUE SE VANA PONCHAR :D
        m = 0
        while m < len(self.burbujas_flotantes):
            x_b, y_b, radio, vel, color, osc = self.burbujas_flotantes[m]
            x_render = x_b + math.sin(self.frame_flote * osc) * 40
    
            self.canvas.create_oval(x_render - radio, y_b - radio, x_render + radio, y_b + radio, fill=color, outline="#FFFFFF", width=3)
          
            self.canvas.create_oval(x_render - radio*0.6, y_b - radio*0.6, x_render - radio*0.2, y_b - radio*0.2, fill="#FFFFFF", outline="")
            m += 1

        # ANIMACION DE BOP DE LAS BURBUJAS
        n = 0
        while n < len(self.burbujas_desvaneciendo):
            x_d, y_d, radio_exp, vida = self.burbujas_desvaneciendo[n]
            
            if vida > 15:
                patron = None
                grosor = 3
            elif vida > 8:
                patron = (6, 6) 
                grosor = 2
            else:
                patron = (2, 10) 
                grosor = 1

            self.canvas.create_oval(x_d - radio_exp, y_d - radio_exp, x_d + radio_exp, y_d + radio_exp, outline="#FFFFFF", width=grosor, dash=patron)
            n += 1

        # MENSAJE DEL FINAL CON LA FRASE FINAL
        if self.estado == "Ganado":
            cx, cy = 500, 250
            mov_flote = math.sin(self.frame_flote * 0.02) * 10
            
            self.canvas.create_text(
                cx, cy + mov_flote, 
                text="Respira profundo.\nLa naturaleza y tú están en calma.", 
                font=("Helvetica", 32, "bold"), fill="#897C9E", justify="center"
            )

        self.canvas.create_text(500, 620, text="SoftRelief", font=("Helvetica", 18, "bold"), fill="#C2B8D1")

    def dibujar_fondo_natural(self):
        """Dibuja un paisaje en capas para ocupar toda la página"""
        # Montañas suaves al fondo
        montanas = [0, 250, 200, 150, 450, 300, 750, 100, 1000, 250, 1000, 750, 0, 750]
        self.canvas.create_polygon(montanas, fill="#E6E1F2", outline="", smooth=True)
        
        montanas2 = [0, 350, 300, 250, 600, 350, 900, 200, 1000, 300, 1000, 750, 0, 750]
        self.canvas.create_polygon(montanas2, fill="#DED6E8", outline="", smooth=True)

        # !!!MEJORAR EL LAGO PARA QUE SE VEA MAS NATURAL
        agua = [0, 420, 500, 380, 1000, 420, 1000, 750, 0, 750]
        self.canvas.create_polygon(agua, fill="#D6EAF8", outline="", smooth=True)
        
        # !!!AGREGAR COCODRILOS, !!!!!
        pasto_izq = [0, 450, 300, 500, 350, 750, 0, 750]
        self.canvas.create_polygon(pasto_izq, fill="#D1E8E2", outline="", smooth=True)
        
        pasto_der = [1000, 480, 700, 530, 650, 750, 1000, 750]
        self.canvas.create_polygon(pasto_der, fill="#C4E0D9", outline="", smooth=True)

    def dibujar_nenufar_y_loto(self, x, y, escala):
        """Nenúfar con flor de loto pastel integrada"""
        radio_x = 60 * escala
        radio_y = 25 * escala
        
        #HOJITAASSSSSSSSS
        self.canvas.create_arc(
            x - radio_x, y - radio_y, x + radio_x, y + radio_y,
            start=40, extent=280, fill="#A3E4D7", outline="#FFFFFF", width=2, style=tk.PIESLICE
        )
        
        # PETALOS DEL FONDO !!!FALATA METERLES ANIMACION PARA QUE SE VEAN SOBRE EL AGUA!!!
        petalos = [
            ("#E1BEE7", -60, -10, -55, -45, -25, -25), 
            ("#E1BEE7",  60, -10,  55, -45,  25, -25), 
            ("#F8BBD0", -45, -25, -30, -70, -10, -45), 
            ("#F8BBD0",  45, -25,  30, -70,  10, -45), 
            ("#FFFFFF", -25, -40,   0, -85,  25, -40)  
        ]
        
        p = 0
        while p < len(petalos):
            color, cx1, cy1, px, py, cx2, cy2 = petalos[p]
            puntos = [
                x, y - (5 * escala), 
                x + (cx1 * escala), y - (5 * escala) + (cy1 * escala),
                x + (px * escala), y - (5 * escala) + (py * escala), 
                x + (cx2 * escala), y - (5 * escala) + (cy2 * escala) 
            ]
            self.canvas.create_polygon(puntos, fill=color, outline="#FFFFFF", width=1, smooth=True)
            p += 1
##DIBUJAR A LAS RANITAS

    def dibujar_ranita(self, x, y, escala, desfase):
        """Ranitas coquetas descansando en el paisaje"""
        self.canvas.create_oval(x - 22*escala, y + 2*escala, x + 22*escala, y + 12*escala, fill="#B5D6CE", outline="")
        
        breathe = math.sin(self.frame_flote * 0.05 + desfase) * (2 * escala)
        self.canvas.create_oval(x - 18*escala, y - 15*escala - breathe, x + 18*escala, y + 8*escala, fill="#86EFAC", outline="#FFFFFF", width=max(1, int(2*escala)))
        
    ##PARPADEO DE LAS RANITAS
        if (self.frame_flote + desfase) % 120 > 8:
            self.canvas.create_oval(x - 16*escala, y - 28*escala - breathe, x - 2*escala, y - 10*escala - breathe, fill="#FFFFFF", outline="#4ADE80", width=max(1, int(2*escala)))
            self.canvas.create_oval(x + 2*escala, y - 28*escala - breathe, x + 16*escala, y - 10*escala - breathe, fill="#FFFFFF", outline="#4ADE80", width=max(1, int(2*escala)))
            self.canvas.create_oval(x - 12*escala, y - 26*escala - breathe, x - 8*escala, y - 20*escala - breathe, fill="#64748B")
            self.canvas.create_oval(x + 4*escala, y - 26*escala - breathe, x + 8*escala, y - 20*escala - breathe, fill="#64748B")
        else:
            self.canvas.create_arc(x - 16*escala, y - 22*escala - breathe, x - 2*escala, y - 12*escala - breathe, start=0, extent=180, outline="#4ADE80", width=max(1, int(3*escala)), style=tk.ARC)
            self.canvas.create_arc(x + 2*escala, y - 22*escala - breathe, x + 16*escala, y - 12*escala - breathe, start=0, extent=180, outline="#4ADE80", width=max(1, int(3*escala)), style=tk.ARC)

if __name__ == "__main__":
    app = PaisajeBurbujasPastel()
    app.mainloop()