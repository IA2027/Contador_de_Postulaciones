
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


# ==========================================
# CONFIGURACION GENERAL
# ==========================================

COLOR_FONDO = "#252525"
COLOR_PANEL = "#303030"
COLOR_NARANJA = "#F07818"
COLOR_NARANJA_HOVER = "#FF9138"
COLOR_BLANCO = "#FFFFFF"
COLOR_GRIS = "#BBBBBB"
COLOR_INPUT = "#414141"

TITULO = "ENVÍO DE CV"

# Carpeta permanente para guardar los registros
APP_DIR = Path(os.getenv("APPDATA", str(Path.home())))
APP_DIR = APP_DIR / "EnvioCV"

APP_DIR.mkdir(parents=True, exist_ok=True)

ARCHIVO_DATOS = APP_DIR / "empresas.json"


# ==========================================
# CLASE PRINCIPAL
# ==========================================

class EnvioCV:

    def __init__(self, ventana):

        self.ventana = ventana

        self.ventana.title(TITULO)
        self.ventana.geometry("1050x720")
        self.ventana.minsize(850, 600)
        self.ventana.configure(bg=COLOR_FONDO)

        self.empresas = []

        self.cargar_datos()

        self.configurar_estilos()
        self.crear_interfaz()
        self.actualizar_tabla()

    # ======================================
    # ESTILOS
    # ======================================

    def configurar_estilos(self):

        estilo = ttk.Style()

        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            background=COLOR_PANEL,
            foreground=COLOR_BLANCO,
            fieldbackground=COLOR_PANEL,
            rowheight=38,
            font=("Segoe UI", 12),
            borderwidth=0
        )

        estilo.configure(
            "Treeview.Heading",
            background=COLOR_NARANJA,
            foreground=COLOR_BLANCO,
            font=("Segoe UI", 12, "bold"),
            padding=12,
            relief="flat"
        )

        estilo.map(
            "Treeview",
            background=[("selected", COLOR_NARANJA)],
            foreground=[("selected", COLOR_BLANCO)]
        )

        estilo.map(
            "Treeview.Heading",
            background=[("active", COLOR_NARANJA_HOVER)]
        )

    # ======================================
    # CREAR INTERFAZ
    # ======================================

    def crear_interfaz(self):

        # TITULO

        encabezado = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        encabezado.pack(fill="x", padx=30, pady=(25, 5))

        tk.Label(
            encabezado,
            text="ENVÍO DE CV",
            font=("Segoe UI", 28, "bold"),
            fg=COLOR_NARANJA,
            bg=COLOR_FONDO
        ).pack(anchor="center")

        tk.Label(
            encabezado,
            text="Registro y seguimiento de empresas y postulaciones",
            font=("Segoe UI", 12),
            fg=COLOR_GRIS,
            bg=COLOR_FONDO
        ).pack(pady=(3, 15))

        # CONTADOR

        self.label_contador = tk.Label(
            self.ventana,
            text="EMPRESAS REGISTRADAS: 0",
            font=("Segoe UI", 13, "bold"),
            fg=COLOR_BLANCO,
            bg=COLOR_PANEL,
            pady=12
        )

        self.label_contador.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # PANEL DE REGISTRO

        panel = tk.Frame(
            self.ventana,
            bg=COLOR_PANEL,
            padx=20,
            pady=18
        )

        panel.pack(
            fill="x",
            padx=30,
            pady=10
        )

        tk.Label(
            panel,
            text="REGISTRAR EMPRESA",
            font=("Segoe UI", 15, "bold"),
            fg=COLOR_NARANJA,
            bg=COLOR_PANEL
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(0, 15)
        )

        # EMPRESA

        tk.Label(
            panel,
            text="Empresa",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_BLANCO,
            bg=COLOR_PANEL
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        self.entrada_empresa = tk.Entry(
            panel,
            font=("Segoe UI", 13),
            bg=COLOR_INPUT,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            width=28
        )

        self.entrada_empresa.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=(0, 15),
            ipady=9
        )

        # EMAIL

        tk.Label(
            panel,
            text="Correo electrónico",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_BLANCO,
            bg=COLOR_PANEL
        ).grid(
            row=1,
            column=1,
            sticky="w",
            pady=5
        )

        self.entrada_email = tk.Entry(
            panel,
            font=("Segoe UI", 13),
            bg=COLOR_INPUT,
            fg=COLOR_BLANCO,
            insertbackground=COLOR_BLANCO,
            relief="flat",
            width=32
        )

        self.entrada_email.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(0, 15),
            ipady=9
        )

        # BOTONES

       # BOTONES EN UNA FILA INDEPENDIENTE

        self.crear_boton(
    panel,
    "AGREGAR",
    self.agregar_empresa,
    0,
    3
)

        self.crear_boton(
            panel,
            "ACTUALIZAR",
            self.actualizar_empresa,
        1,
        3
        )

        self.crear_boton(
    panel,
    "ELIMINAR",
    self.eliminar_empresa,
    2,
    3
)

        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=1)

        # PANEL DE LISTADO

        listado = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        listado.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        tk.Label(
            listado,
            text="LISTADO DE EMPRESAS",
            font=("Segoe UI", 16, "bold"),
            fg=COLOR_BLANCO,
            bg=COLOR_FONDO
        ).pack(
            anchor="w",
            pady=(5, 12)
        )

        # TABLA

        columnas = ("empresa", "email")

        self.tabla = ttk.Treeview(
            listado,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        self.tabla.heading(
            "empresa",
            text="EMPRESA"
        )

        self.tabla.heading(
            "email",
            text="CORREO ELECTRÓNICO"
        )

        self.tabla.column(
            "empresa",
            width=400,
            anchor="w"
        )

        self.tabla.column(
            "email",
            width=450,
            anchor="w"
        )

        scrollbar = ttk.Scrollbar(
            listado,
            orient="vertical",
            command=self.tabla.yview
        )

        self.tabla.configure(
            yscrollcommand=scrollbar.set
        )

        self.tabla.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tabla.bind(
            "<<TreeviewSelect>>",
            self.seleccionar_empresa
        )

        # BOTONES DE EXPORTACION

        pie = tk.Frame(
            self.ventana,
            bg=COLOR_FONDO
        )

        pie.pack(
            fill="x",
            padx=30,
            pady=(5, 20)
        )

        self.crear_boton(
            pie,
            "DESCARGAR PDF",
            self.exportar_pdf,
            0,
            0
        )

        self.crear_boton(
            pie,
            "DESCARGAR TXT",
            self.exportar_txt,
            1,
            0
        )

        # PIE DE PAGINA

        tk.Label(
            self.ventana,
            text="ENVÍO DE CV | SISTEMA DE REGISTRO PERSONAL",
            font=("Segoe UI", 9),
            fg=COLOR_GRIS,
            bg=COLOR_FONDO
        ).pack(pady=(0, 10))

    # ======================================
    # CREAR BOTONES
    # ======================================

    def crear_boton(
        self,
        padre,
        texto,
        comando,
        columna,
        fila
    ):

        boton = tk.Button(
            padre,
            text=texto,
            command=comando,
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_NARANJA,
            fg=COLOR_BLANCO,
            activebackground=COLOR_NARANJA_HOVER,
            activeforeground=COLOR_BLANCO,
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=11,
            width=16
        )

        boton.grid(
            row=fila,
            column=columna,
            padx=6,
            pady=5,
            sticky="ew"
        )

        boton.bind(
            "<Enter>",
            lambda e: boton.config(
                bg=COLOR_NARANJA_HOVER
            )
        )

        boton.bind(
            "<Leave>",
            lambda e: boton.config(
                bg=COLOR_NARANJA
            )
        )

    # ======================================
    # AGREGAR EMPRESA
    # ======================================

    def agregar_empresa(self):

        empresa = self.entrada_empresa.get().strip()
        email = self.entrada_email.get().strip()

        if not empresa or not email:

            messagebox.showwarning(
                "Datos incompletos",
                "Completá el nombre de la empresa y el correo."
            )

            return

        if "@" not in email or "." not in email.split("@")[-1]:

            messagebox.showwarning(
                "Correo inválido",
                "Ingresá una dirección de correo válida."
            )

            return

        # Evitar duplicados

        for registro in self.empresas:

            if (
                registro["empresa"].lower() == empresa.lower()
                and registro["email"].lower() == email.lower()
            ):

                messagebox.showwarning(
                    "Registro duplicado",
                    "Esta empresa y correo ya están registrados."
                )

                return

        self.empresas.append({
            "empresa": empresa,
            "email": email
        })

        self.guardar_datos()
        self.actualizar_tabla()
        self.limpiar_campos()

        messagebox.showinfo(
            "Registro exitoso",
            "La empresa fue agregada correctamente."
        )

    # ======================================
    # SELECCIONAR REGISTRO
    # ======================================

    def seleccionar_empresa(self, evento):

        seleccion = self.tabla.selection()

        if not seleccion:
            return

        valores = self.tabla.item(
            seleccion[0],
            "values"
        )

        self.entrada_empresa.delete(0, tk.END)
        self.entrada_empresa.insert(0, valores[0])

        self.entrada_email.delete(0, tk.END)
        self.entrada_email.insert(0, valores[1])

    # ======================================
    # ACTUALIZAR REGISTRO
    # ======================================

    def actualizar_empresa(self):

        seleccion = self.tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                "Seleccionar empresa",
                "Primero seleccioná una empresa de la tabla."
            )

            return

        empresa = self.entrada_empresa.get().strip()
        email = self.entrada_email.get().strip()

        if not empresa or not email:

            messagebox.showwarning(
                "Datos incompletos",
                "Completá ambos campos."
            )

            return

        if "@" not in email or "." not in email.split("@")[-1]:

            messagebox.showwarning(
                "Correo inválido",
                "Ingresá un correo electrónico válido."
            )

            return

        item = seleccion[0]
        indice = int(item)

        for i, registro in enumerate(self.empresas):

            if i != indice and (
                registro["empresa"].lower() == empresa.lower()
                and registro["email"].lower() == email.lower()
            ):

                messagebox.showwarning(
                    "Registro duplicado",
                    "Esta empresa y correo ya están registrados."
                )

                return

        self.empresas[indice] = {
            "empresa": empresa,
            "email": email
        }

        self.guardar_datos()
        self.actualizar_tabla()
        self.limpiar_campos()

        messagebox.showinfo(
            "Actualización",
            "El registro fue actualizado correctamente."
        )

    # ======================================
    # ELIMINAR REGISTRO
    # ======================================

    def eliminar_empresa(self):

        seleccion = self.tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                "Seleccionar empresa",
                "Seleccioná una empresa para eliminar."
            )

            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Querés eliminar este registro?"
        )

        if not confirmar:
            return

        indice = int(seleccion[0])

        self.empresas.pop(indice)

        self.guardar_datos()
        self.actualizar_tabla()
        self.limpiar_campos()

    # ======================================
    # LIMPIAR CAMPOS
    # ======================================

    def limpiar_campos(self):

        self.entrada_empresa.delete(0, tk.END)
        self.entrada_email.delete(0, tk.END)

        seleccion = self.tabla.selection()

        if seleccion:
            self.tabla.selection_remove(*seleccion)

    # ======================================
    # ACTUALIZAR TABLA
    # ======================================

    def actualizar_tabla(self):

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for indice, registro in enumerate(self.empresas):

            self.tabla.insert(
                "",
                "end",
                iid=str(indice),
                values=(
                    registro["empresa"],
                    registro["email"]
                )
            )

        cantidad = len(self.empresas)

        self.label_contador.config(
            text=f"EMPRESAS REGISTRADAS: {cantidad}"
        )

    # ======================================
    # GUARDAR DATOS
    # ======================================

    def guardar_datos(self):

        try:

            with open(
                ARCHIVO_DATOS,
                "w",
                encoding="utf-8"
            ) as archivo:

                json.dump(
                    self.empresas,
                    archivo,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError as error:

            messagebox.showerror(
                "Error al guardar",
                f"No se pudieron guardar los datos:\n{error}"
            )

    # ======================================
    # CARGAR DATOS
    # ======================================

    def cargar_datos(self):

        if ARCHIVO_DATOS.exists():

            try:

                with open(
                    ARCHIVO_DATOS,
                    "r",
                    encoding="utf-8"
                ) as archivo:

                    datos = json.load(archivo)

                    if isinstance(datos, list) and all(
                        isinstance(registro, dict)
                        and isinstance(registro.get("empresa"), str)
                        and isinstance(registro.get("email"), str)
                        for registro in datos
                    ):

                        self.empresas = datos

                    else:

                        messagebox.showwarning(
                            "Archivo de datos",
                            "El archivo de registros tiene un formato inválido."
                        )

            except (OSError, json.JSONDecodeError) as error:

                messagebox.showerror(
                    "Error de lectura",
                    f"No se pudieron cargar los registros:\n{error}"
                )

    # ======================================
    # EXPORTAR TXT
    # ======================================

    def exportar_txt(self):

        if not self.empresas:

            messagebox.showwarning(
                "Sin registros",
                "No hay empresas para exportar."
            )

            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
            initialfile="Listado_Empresas_CV.txt"
        )

        if not ruta:
            return

        try:

            with open(
                ruta,
                "w",
                encoding="utf-8"
            ) as archivo:

                archivo.write("REGISTRO DE ENVÍO DE CV\n")
                archivo.write("=" * 55 + "\n\n")

                archivo.write(
                    f"Fecha de exportación: "
                    f"{datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                )

                for numero, registro in enumerate(
                    self.empresas,
                    start=1
                ):

                    archivo.write(
                        f"{numero}. EMPRESA: {registro['empresa']}\n"
                    )

                    archivo.write(
                        f"   EMAIL: {registro['email']}\n\n"
                    )

                archivo.write("=" * 55 + "\n")
                archivo.write(
                    f"TOTAL DE EMPRESAS: {len(self.empresas)}\n"
                )

            messagebox.showinfo(
                "Exportación exitosa",
                "El archivo TXT fue creado correctamente."
            )

        except OSError as error:

            messagebox.showerror(
                "Error",
                f"No se pudo crear el archivo:\n{error}"
            )

    # ======================================
    # EXPORTAR PDF
    # ======================================

    def exportar_pdf(self):

        if not self.empresas:

            messagebox.showwarning(
                "Sin registros",
                "No hay empresas para exportar."
            )

            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            initialfile="Listado_Empresas_CV.pdf"
        )

        if not ruta:
            return

        try:

            documento = SimpleDocTemplate(
                ruta,
                pagesize=landscape(A4),
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            estilos = getSampleStyleSheet()

            titulo = ParagraphStyle(
                "TituloPersonalizado",
                parent=estilos["Title"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=28,
                textColor=colors.HexColor(COLOR_NARANJA),
                alignment=TA_CENTER,
                spaceAfter=12
            )

            normal = ParagraphStyle(
                "TextoTabla",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=11,
                leading=15,
                textColor=colors.HexColor("#252525")
            )

            elementos = []

            elementos.append(
                Paragraph("ENVÍO DE CV", titulo)
            )

            elementos.append(
                Paragraph(
                    "Registro de empresas y correos electrónicos",
                    estilos["Normal"]
                )
            )

            elementos.append(Spacer(1, 20))

            elementos.append(
                Paragraph(
                    "Fecha de exportación: "
                    + datetime.now().strftime("%d/%m/%Y %H:%M"),
                    estilos["Normal"]
                )
            )

            elementos.append(Spacer(1, 15))

            datos = [
                [
                    "N°",
                    "EMPRESA",
                    "CORREO ELECTRÓNICO"
                ]
            ]

            for numero, registro in enumerate(
                self.empresas,
                start=1
            ):

                empresa = registro["empresa"].replace(
                    "&", "&amp;"
                ).replace("<", "&lt;").replace(">", "&gt;")

                email = registro["email"].replace(
                    "&", "&amp;"
                ).replace("<", "&lt;").replace(">", "&gt;")

                datos.append([
                    str(numero),
                    Paragraph(empresa, normal),
                    Paragraph(email, normal)
                ])

            tabla = Table(
                datos,
                colWidths=[45, 310, 400],
                repeatRows=1
            )

            tabla.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(COLOR_NARANJA)
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, 0),
                        12
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "LEFT"
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.HexColor("#F2F2F2")
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#EEEEEE")
                        ]
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#CCCCCC")
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    )
                ])
            )

            elementos.append(tabla)

            elementos.append(Spacer(1, 20))

            elementos.append(
                Paragraph(
                    f"TOTAL DE EMPRESAS REGISTRADAS: "
                    f"{len(self.empresas)}",
                    estilos["Heading2"]
                )
            )

            documento.build(elementos)

            messagebox.showinfo(
                "PDF generado",
                "El documento PDF fue creado correctamente."
            )

        except Exception as error:

            messagebox.showerror(
                "Error al generar PDF",
                f"No se pudo crear el PDF:\n{error}"
            )


# ==========================================
# INICIAR APLICACION
# ==========================================

if __name__ == "__main__":

    ventana = tk.Tk()

    aplicacion = EnvioCV(ventana)

    ventana.mainloop()
