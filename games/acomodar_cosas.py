import customtkinter as ctk
import tkinter as tk
import math
import random

class LibreriaZen(ctk.CTkToplevel):

    def __init__(self, master=None):
        super().__init__(master)
        
        # CONFIGURACION DE LA VENTANA
        self.title("Microdescansos 3: Acomodar libros")
        self.geometry("1000x750")
        self.configure(fg_color="#F4EFFF") # COLOR DE LA PARED, O EL FONDO

        # ESTADO DEL JUEGO
        self.estado = "Jugando"      
        self.libro_activo = -1
        self.offset_x = 0
        self.offset_y = 0
        
        self.x_origen = 0
        self.y_origen = 0

        self.y_repisa = 580
        # LOS ESPACIOS DONDE SE VAN A PONER LOS LIBROS EN TOTAL 8
        self.slots = [220, 290, 360, 430, 500, 570, 640, 710] 

        self.destellos = [] 
        self.frame_animacion = 0

        ##AQUI VAMOS A MODELAR MIS LIBROS, SUS TAMANOS Y TODO ESO
        self.libros = [
            [0, 0, 50, 100, "#DDEFFF", 1], 
            [0, 0, 50, 130, "#D9D4FF", 2], 
            [0, 0, 50, 160, "#D8C8FF", 3], 
            [0, 0, 50, 190, "#CDB7FF", 4], 
            [0, 0, 50, 220, "#C2EFFF", 5], 
            [0, 0, 50, 250, "#B9E8F2", 6], 
            [0, 0, 50, 280, "#B79CF2", 7], 
            [0, 0, 50, 310, "#A56BE8", 8]          ]

        # AQUI SE DESORDENAN LOS LIBROS
        idx = 0
        while idx < len(self.libros):
            # AQUI SE HACEN LAS POSICIONES DE LOS LIBROS
            self.libros[idx][0] = random.randint(150, 750)
            self.libros[idx][1] = random.randint(150, 300)
            idx += 1

        # INTERFAZ GRAFICA-
        self.frame_cabecera = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cabecera.pack(pady=(15, 5))

        self.titulo = ctk.CTkLabel(self.frame_cabecera, text="Un Poco a la Izquierda", font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"), text_color="#5D576B")
        self.titulo.pack()
        
        self.subtitulo = ctk.CTkLabel(self.frame_cabecera, text="Acomoda los 8 libros en la repisa del más bajito al más alto.", font=ctk.CTkFont(size=16), text_color="#8A9CA8")
        self.subtitulo.pack(pady=(0, 5))

        self.canvas = tk.Canvas(self, bg="#F4EFFF", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)

        # EDONDE SE AGARRA Y SE ARRASTRA
        self.canvas.bind("<Button-1>", self.al_presionar)
        self.canvas.bind("<B1-Motion>", self.al_arrastrar)
        self.canvas.bind("<ButtonRelease-1>", self.al_soltar)

        # SE INICIA LA ANIMACION
        self.bucle_animacion()

    # MOTOR DE LA ANIMACION
    def bucle_animacion(self):
        self.frame_animacion += 1
        self.actualizar_particulas()
        self.dibujar_escena()
        self.after(25, self.bucle_animacion)

    def actualizar_particulas(self):
        j = 0
        while j < len(self.destellos):
            self.destellos[j][0] += self.destellos[j][2] 
            self.destellos[j][1] += self.destellos[j][3] 
            self.destellos[j][4] -= 1 
            self.destellos[j][3] += 0.2 # GRAVEDAD
            
            if self.destellos[j][4] <= 0:
                self.destellos.pop(j)
            else:
                j += 1

    def generar_brillitos(self, x, y):
        i = 0
        colores = ["#FFF59D", "#FFFFFF", "#FF96A4", "#80DEEA"]
        while i < 15:
            vx = random.uniform(-4, 4)
            vy = random.uniform(-6, 0)
            vida = random.randint(10, 25)
            color = random.choice(colores)
            self.destellos.append([x, y, vx, vy, vida, color])
            i += 1

    # AQUI ES DONDE ESTA LA LOGICA DEL JUEGO
    def al_presionar(self, evento):
        if self.estado == "Jugando":
            mx, my = evento.x, evento.y
            
            i = len(self.libros) - 1
            self.libro_activo = -1
            
            while i >= 0:
                x, y, w, h = self.libros[i][0:4]
                
                if x <= mx <= x + w and y <= my <= y + h:
                    self.libro_activo = i
                    self.offset_x = mx - x
                    self.offset_y = my - y
                    self.x_origen = x
                    self.y_origen = y
                    
                    # TTRAER ENFRENTE LOS LIBROS
                    libro_sel = self.libros.pop(i)
                    self.libros.append(libro_sel)
                    self.libro_activo = len(self.libros) - 1
                    break
                i -= 1

    def al_arrastrar(self, evento):
        if self.libro_activo != -1 and self.estado == "Jugando":
            x_nuevo = evento.x - self.offset_x
            y_nuevo = evento.y - self.offset_y
            self.libros[self.libro_activo][0] = x_nuevo
            self.libros[self.libro_activo][1] = y_nuevo

    def al_soltar(self, evento):
        if self.libro_activo != -1 and self.estado == "Jugando":
            x_actual = self.libros[self.libro_activo][0]
            h_libro = self.libros[self.libro_activo][3]
            y_base_libro = self.libros[self.libro_activo][1] + h_libro
            
            # AQUI ES DONDE SE ACOMODA EL LIBRO EN EL SLOT MAS CERCANO QUE TENGA
            slot_mas_cercano = -1
            distancia_min = 9999
            s = 0
            while s < len(self.slots):
                dist = abs(x_actual - self.slots[s])
                if dist < distancia_min:
                    distancia_min = dist
                    slot_mas_cercano = self.slots[s]
                s += 1
                
            #  ESTO ES LO QUE ATRAE EL LIBRO A LA RESPISA Y LO DEJA EN EL SLOT MAS CERCANO QUE TENGA CUANDO EL USUARIO SE ACERCA LO SUFICIENTE
            if distancia_min < 40 and (self.y_repisa - 150) < y_base_libro < (self.y_repisa + 100):
                
                # AQUI SE REVISA SI EL SLOT YA ESTA OCUPADO POR OTRO LIBRO
                ocupante_idx = -1
                k = 0
                while k < len(self.libros):
                    if k != self.libro_activo:
                        o_x = self.libros[k][0]
                        o_y_base = self.libros[k][1] + self.libros[k][3]
                        if o_x == slot_mas_cercano and o_y_base == self.y_repisa:
                            ocupante_idx = k
                    k += 1
##SE HACE EL CAMBIO POR EL LIBRO QUE YA ESTA AHI
                if ocupante_idx != -1:
                    self.libros[ocupante_idx][0] = self.x_origen
                    self.libros[ocupante_idx][1] = self.y_origen

            ##SE ACOMODA EL LIBRO ACTUAL EN EL LUGAR
                self.libros[self.libro_activo][0] = slot_mas_cercano
                self.libros[self.libro_activo][1] = self.y_repisa - h_libro
                self.generar_brillitos(slot_mas_cercano + 25, self.y_repisa - 20)
            
            self.libro_activo = -1
            self.verificar_victoria()

    def verificar_victoria(self):
        """Revisa que todos estén en la repisa y ordenados por altura"""
        repisa_estado = [-1] * 8 # GUARDAR LA ESTATURA DE CADA LIBRO
        
        i = 0
        while i < len(self.libros):
            x, y, w, h = self.libros[i][0:4]
            en_slot = False
            s = 0
            while s < len(self.slots):
                if x == self.slots[s] and y == self.y_repisa - h:
                    repisa_estado[s] = h
                    en_slot = True
                s += 1
                
            if en_slot == False:
                return # SI AL MENOS UNO NO ESTA EN DONDE DEBE NO SE GANA EL JUEGO
            i += 1

        # REVISAR LAS ALTURAS DE LOS LIBROS QUE ESTEN ACOMODADOS.
        s = 0
        while s < 7:
            # SI HAY UNO MAL NO SE ACABA 
            if repisa_estado[s] > repisa_estado[s+1]:
                return 
            s += 1

        # SI SE ACOMODAN TOOOS LOS LIBROS DE MANERA CORECTA SE GANA AUTOMATICAMENTE
        self.estado = "Ganado"
        self.subtitulo.configure(text="¡Perfecto! Todo está en su lugar.", text_color="#38A169")

    # --- RENDERIZADO VISUAL ---
    def dibujar_escena(self):
        self.canvas.delete("all")
        
        # SE DIBUJA EL FONDO, O MAS CERCANO LA VENTANA
        self.dibujar_fondo_cuarto()

        # REPISA
        self.canvas.create_rectangle(150, self.y_repisa, 830, self.y_repisa + 25, fill="#D2B48C", outline="#5D4037", width=3)
        self.canvas.create_polygon([170, self.y_repisa+25, 810, self.y_repisa+25, 790, self.y_repisa+45, 190, self.y_repisa+45], fill="#A1887F", outline="#5D4037", width=3)
        self.canvas.create_polygon([250, self.y_repisa+45, 270, self.y_repisa+45, 250, self.y_repisa+100], fill="#8D6E63", outline="#5D4037", width=3)
        self.canvas.create_polygon([730, self.y_repisa+45, 710, self.y_repisa+45, 730, self.y_repisa+100], fill="#8D6E63", outline="#5D4037", width=3)

        # DIBUJAR LIBROS 
        i = 0
        while i < len(self.libros):
            x, y, w, h, color, l_id = self.libros[i]
            
            # SOMBRAS
            self.canvas.create_rectangle(x+5, y+5, x+w+5, y+h+5, fill="#D1C4E9", outline="")
            
            # LINEA PRICNIPAL DEL DIBUJO
            self.canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="#2C3E50", width=3)
            

            self.canvas.create_rectangle(x, y, x+w, y+10, fill="#FFFFFF", outline="#2C3E50", width=3)
            self.canvas.create_line(x+10, y, x+10, y+10, fill="#2C3E50", width=1)
            self.canvas.create_line(x+25, y, x+25, y+10, fill="#2C3E50", width=1)
            self.canvas.create_line(x+40, y, x+40, y+10, fill="#2C3E50", width=1)

            # Detalles del lomo (Líneas horizontales)
            self.canvas.create_line(x, y+h-20, x+w, y+h-20, fill="#2C3E50", width=3)
            self.canvas.create_line(x, y+h-30, x+w, y+h-30, fill="#2C3E50", width=3)
            
            i += 1

        #  DIBUJAR DESTELLOS
        k = 0
        while k < len(self.destellos):
            x_d, y_d, vx, vy, vida, color_d = self.destellos[k]
            tam = vida / 3
            self.canvas.create_oval(x_d - tam, y_d - tam, x_d + tam, y_d + tam, fill=color_d, outline="")
            k += 1

        #  CUANDO SE GANA LP QIE SE MUESTRA
        if self.estado == "Has ganado!!!":
            s = 0
            while s < len(self.slots):
                # Flotación rítmica
                mov_y = math.sin(self.frame_animacion * 0.1 + s) * 10
                self.dibujar_estrella_destripando(self.slots[s] + 25, 200 + mov_y)
                s += 1

    def dibujar_fondo_cuarto(self):
        """Dibuja elementos decorativos de fondo"""
        self.canvas.create_arc(350, 50, 650, 350, start=0, extent=180, fill="#D6EAF8", outline="#BDC3C7", width=5)
        self.canvas.create_rectangle(350, 200, 650, 450, fill="#D6EAF8", outline="#BDC3C7", width=5)
        # rejillas de la ventana
        self.canvas.create_line(500, 50, 500, 450, fill="#BDC3C7", width=5)
        self.canvas.create_line(350, 250, 650, 250, fill="#BDC3C7", width=5)
        # NUBES
        nubes = [(400, 150), (550, 120), (450, 300), (580, 280)]
        n = 0
        while n < len(nubes):
            nx, ny = nubes[n]
            mov = math.sin(self.frame_animacion * 0.02 + n) * 5
            self.canvas.create_oval(nx, ny, nx+60, ny+30, fill="#FFFFFF", outline="")
            self.canvas.create_oval(nx+20, ny-15, nx+70, ny+25, fill="#FFFFFF", outline="")
            self.canvas.create_oval(nx+50, ny+5, nx+90, ny+30, fill="#FFFFFF", outline="")
            n += 1

    def dibujar_estrella_destripando(self, x, y):
        """Dibuja una estrella de 5 picos con trazo grueso y carita amigable"""
        puntos = [
            x, y-30, x+10, y-10, x+32, y-10, x+15, y+5, 
            x+22, y+28, x, y+15, x-22, y+28, x-15, y+5, 
            x-32, y-10, x-10, y-10
        ]
        
        # SE DIBUJA LAS ESTRELLAS
        self.canvas.create_polygon(puntos, fill="#FFEB3B", outline="#2C3E50", width=4, smooth=False)
        
        
        self.canvas.create_oval(x-10, y-5, x-4, y+5, fill="#2C3E50")
        self.canvas.create_oval(x+4, y-5, x+10, y+5, fill="#2C3E50")
        self.canvas.create_oval(x-8, y-3, x-6, y-1, fill="#FFFFFF")
        self.canvas.create_oval(x+6, y-3, x+8, y-1, fill="#FFFFFF")
        self.canvas.create_arc(x-8, y+5, x+8, y+15, start=180, extent=180, outline="#2C3E50", width=3, style=tk.ARC)

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()

    app = LibreriaZen(master=root)
    app.protocol("WM_DELETE_WINDOW", root.destroy)

    root.mainloop()