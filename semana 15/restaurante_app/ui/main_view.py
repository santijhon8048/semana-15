import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from modelos.producto import Producto
from servicios.restaurante_servicio import RestauranteServicio


class MainView(ttk.Frame):
    def __init__(self, master: tk.Misc, servicio: RestauranteServicio, guardar_datos) -> None:
        super().__init__(master, padding=18)
        self.servicio = servicio
        self.guardar_datos = guardar_datos
        self.venta_usuario = tk.StringVar()
        self.venta_producto = tk.StringVar()
        self.venta_cantidad = tk.StringVar(value="1")
        self.venta_total = tk.StringVar(value="Total estimado: $0.00")
        self.venta_estado = tk.StringVar(value="Seleccione usuario, producto y cantidad.")
        self._usuarios_venta: dict[str, str] = {}
        self._productos_venta: dict[str, str] = {}
        self.iconos: dict[str, tk.PhotoImage] = {}
        self._cargar_iconos()
        self._construir()
        self._actualizar_tablas()

    def _cargar_iconos(self) -> None:
        ruta_assets = Path(__file__).resolve().parent.parent / "assets"
        for nombre in ("logo_panel", "usuario", "producto", "venta"):
            try:
                imagen = tk.PhotoImage(file=str(ruta_assets / f"{nombre}.png"))
                self.iconos[nombre] = imagen
            except tk.TclError:
                continue

    def _construir(self) -> None:
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        fondo = "#f3f6f2"
        texto = "#20332f"
        estilo.configure("App.TFrame", background=fondo)
        estilo.configure("Titulo.TLabel", background=fondo, foreground="#183a35")
        estilo.configure(
            "Estado.TLabel",
            background="#e2eee8",
            foreground="#245746",
            padding=(10, 8),
        )
        estilo.configure("TNotebook", background=fondo, borderwidth=0)
        estilo.configure(
            "TNotebook.Tab",
            background="#dce5df",
            foreground="#38514a",
            padding=(16, 8),
            font=("Segoe UI", 10, "bold"),
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", "#176b5b")],
            foreground=[("selected", "#ffffff")],
        )
        estilo.configure(
            "Treeview",
            rowheight=32,
            font=("Segoe UI", 10),
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground=texto,
        )
        estilo.configure(
            "Treeview.Heading",
            background="#315e52",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(8, 7),
        )
        estilo.map(
            "Treeview",
            background=[("selected", "#b9d8c9")],
            foreground=[("selected", "#183a35")],
        )
        for nombre, color, activo in (
            ("Registrar", "#176b5b", "#105447"),
            ("Consultar", "#3d6380", "#304f66"),
            ("Actualizar", "#a86724", "#87521b"),
            ("Limpiar", "#64756e", "#4f5e58"),
            ("Eliminar", "#b74c43", "#963b34"),
        ):
            estilo.configure(
                f"{nombre}.TButton",
                background=color,
                foreground="#ffffff",
                padding=(10, 7),
                borderwidth=0,
            )
            estilo.map(
                f"{nombre}.TButton",
                background=[("active", activo), ("pressed", activo)],
                foreground=[("disabled", "#e5e9e6")],
            )
        self.configure(style="App.TFrame")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        encabezado = ttk.Frame(self, style="App.TFrame")
        encabezado.grid(row=0, column=0, sticky="w", pady=(0, 12))
        if "logo_panel" in self.iconos:
            ttk.Label(encabezado, image=self.iconos["logo_panel"]).pack(
                side="left", padx=(0, 10)
            )
        ttk.Label(
            encabezado,
            text="Panel principal",
            style="Titulo.TLabel",
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, sticky="nsew")
        self.productos_tab = ttk.Frame(self.tabs, padding=12)
        self.usuarios_tab = ttk.Frame(self.tabs, padding=12)
        self.ventas_tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.productos_tab, text="Productos")
        self.tabs.add(self.usuarios_tab, text="Usuarios")
        self.tabs.add(self.ventas_tab, text="Ventas")
        self._construir_productos()
        self._construir_usuarios()
        self._construir_ventas()

    def _construir_ventas(self) -> None:
        tab = self.ventas_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        formulario = ttk.LabelFrame(tab, text="Registrar venta", padding=12)
        formulario.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        formulario.columnconfigure(0, weight=1)
        formulario.columnconfigure(1, weight=1)

        etiqueta_usuario = ttk.Label(formulario, text="Usuario")
        if "usuario" in self.iconos:
            etiqueta_usuario.configure(image=self.iconos["usuario"], compound="left")
        etiqueta_usuario.grid(row=0, column=0, sticky="w", padx=(0, 12))

        etiqueta_producto = ttk.Label(formulario, text="Producto")
        if "producto" in self.iconos:
            etiqueta_producto.configure(image=self.iconos["producto"], compound="left")
        etiqueta_producto.grid(row=0, column=1, sticky="w")

        self.venta_usuario_combo = ttk.Combobox(
            formulario, textvariable=self.venta_usuario, state="readonly"
        )
        self.venta_usuario_combo.grid(
            row=1, column=0, sticky="ew", padx=(0, 12), pady=(4, 10)
        )
        self.venta_producto_combo = ttk.Combobox(
            formulario, textvariable=self.venta_producto, state="readonly"
        )
        self.venta_producto_combo.grid(
            row=1, column=1, sticky="ew", pady=(4, 10)
        )

        ttk.Label(formulario, text="Cantidad").grid(row=2, column=0, sticky="w")
        ttk.Label(formulario, textvariable=self.venta_total).grid(
            row=2, column=1, sticky="e"
        )
        self.venta_cantidad_spin = ttk.Spinbox(
            formulario,
            from_=1,
            to=9999,
            textvariable=self.venta_cantidad,
            width=10,
            command=self._actualizar_total_estimado,
        )
        self.venta_cantidad_spin.grid(row=3, column=0, sticky="w", pady=(4, 10))
        self.venta_cantidad_spin.bind(
            "<KeyRelease>", lambda _evento: self._actualizar_total_estimado()
        )
        self.venta_usuario_combo.bind(
            "<<ComboboxSelected>>", lambda _evento: self._actualizar_total_estimado()
        )
        self.venta_producto_combo.bind(
            "<<ComboboxSelected>>", lambda _evento: self._actualizar_total_estimado()
        )

        icono_venta = self.iconos.get("venta")
        ttk.Button(
            formulario,
            text="Registrar venta",
            image=icono_venta,
            compound="left" if icono_venta else "none",
            command=self._registrar_venta,
            style="Registrar.TButton",
        ).grid(row=3, column=1, sticky="e", pady=(4, 10))

        self.ventas_tree = ttk.Treeview(
            tab,
            columns=("codigo", "fecha", "usuario", "producto", "cantidad", "unitario", "total"),
            show="headings",
        )
        encabezados = {
            "codigo": "Venta",
            "fecha": "Fecha",
            "usuario": "Usuario",
            "producto": "Producto",
            "cantidad": "Cantidad",
            "unitario": "P. unitario",
            "total": "Total",
        }
        for columna, titulo in encabezados.items():
            self.ventas_tree.heading(columna, text=titulo)
        self.ventas_tree.column("codigo", width=90, anchor="center")
        self.ventas_tree.column("fecha", width=145, anchor="center")
        self.ventas_tree.column("usuario", width=110)
        self.ventas_tree.column("producto", width=190)
        self.ventas_tree.column("cantidad", width=75, anchor="center")
        self.ventas_tree.column("unitario", width=100, anchor="e")
        self.ventas_tree.column("total", width=100, anchor="e")
        barra = ttk.Scrollbar(tab, orient="vertical", command=self.ventas_tree.yview)
        self.ventas_tree.configure(yscrollcommand=barra.set)
        self.ventas_tree.grid(row=1, column=0, sticky="nsew")
        barra.grid(row=1, column=1, sticky="ns")
        ttk.Label(tab, textvariable=self.venta_estado, style="Estado.TLabel").grid(
            row=2, column=0, sticky="ew", pady=(8, 0)
        )

    def _construir_productos(self) -> None:
        tab = self.productos_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        formulario = ttk.LabelFrame(tab, text="Datos del producto", padding=10)
        formulario.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)
        formulario.columnconfigure(5, weight=1)
        campos = ["Código", "Nombre", "Categoría", "Precio", "Stock"]
        self.producto_vars = {campo: tk.StringVar() for campo in campos}
        for columna, campo in enumerate(campos):
            posicion = columna * 2
            ttk.Label(formulario, text=campo).grid(
                row=0, column=posicion, padx=(4, 6), sticky="w"
            )
            ttk.Entry(formulario, textvariable=self.producto_vars[campo], width=16).grid(
                row=1, column=posicion, columnspan=2, padx=(4, 10), pady=(4, 0), sticky="ew"
            )
        acciones = ttk.Frame(formulario)
        acciones.grid(row=2, column=0, columnspan=10, pady=(12, 0), sticky="w")
        ttk.Button(
            acciones,
            text="Registrar",
            command=self._agregar_producto,
            style="Registrar.TButton",
        ).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(
            acciones,
            text="Cargar / consultar",
            command=self._cargar_producto,
            style="Consultar.TButton",
        ).pack(
            side="left", padx=6
        )
        ttk.Button(
            acciones,
            text="Actualizar",
            command=self._actualizar_producto,
            style="Actualizar.TButton",
        ).pack(
            side="left", padx=6
        )
        ttk.Button(
            acciones,
            text="Limpiar",
            command=self._limpiar_producto,
            style="Limpiar.TButton",
        ).pack(
            side="left", padx=6
        )
        self.producto_estado = tk.StringVar(value="Seleccione una acción para comenzar.")
        ttk.Label(tab, textvariable=self.producto_estado, style="Estado.TLabel").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        self.productos_tree = ttk.Treeview(
            tab, columns=("codigo", "nombre", "categoria", "precio", "stock"), show="headings"
        )
        for columna, titulo in zip(self.productos_tree["columns"], campos):
            self.productos_tree.heading(columna, text=titulo)
        self.productos_tree.column("codigo", width=100, anchor="center")
        self.productos_tree.column("nombre", width=180)
        self.productos_tree.column("categoria", width=140)
        self.productos_tree.column("precio", width=90, anchor="e")
        self.productos_tree.column("stock", width=80, anchor="center")
        barra = ttk.Scrollbar(tab, orient="vertical", command=self.productos_tree.yview)
        self.productos_tree.configure(yscrollcommand=barra.set)
        self.productos_tree.grid(row=1, column=0, sticky="nsew")
        barra.grid(row=1, column=1, sticky="ns")
        ttk.Button(
            tab,
            text="Eliminar seleccionado",
            command=self._eliminar_producto,
            style="Eliminar.TButton",
        ).grid(
            row=3, column=0, sticky="e", pady=(10, 0)
        )

    def _construir_usuarios(self) -> None:
        tab = self.usuarios_tab
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        formulario = ttk.LabelFrame(tab, text="Usuarios registrados", padding=10)
        formulario.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(
            formulario,
            text="Consulta la información disponible para iniciar sesión.",
        ).grid(row=0, column=0, sticky="w")
        campos = ["Identificación", "Nombre", "Correo", "Nombre de usuario"]
        self.usuarios_tree = ttk.Treeview(
            tab,
            columns=("identificacion", "nombre", "correo", "nombre_usuario"),
            show="headings",
        )
        for columna, titulo in zip(self.usuarios_tree["columns"], campos):
            self.usuarios_tree.heading(columna, text=titulo)
        self.usuarios_tree.grid(row=1, column=0, sticky="nsew")

    def _agregar_producto(self) -> None:
        try:
            producto = self._producto_desde_formulario()
            if not self.servicio.registrar_producto(producto):
                raise ValueError("El código ya está registrado.")
            self.guardar_datos()
            self._limpiar_producto()
            self._actualizar_tablas()
            self.producto_estado.set(f"Producto {producto.codigo} registrado correctamente.")
        except (ValueError, TypeError) as error:
            messagebox.showerror("Producto inválido", str(error))

    def _cargar_producto(self) -> None:
        producto = self.servicio.buscar_producto(self.producto_vars["Código"].get())
        if producto is None:
            messagebox.showerror("Producto no encontrado", "No existe un producto con ese código.")
            return
        self._mostrar_producto(producto)
        self.producto_estado.set(f"Producto {producto.codigo} cargado para consulta o actualización.")

    def _actualizar_producto(self) -> None:
        try:
            codigo = self.producto_vars["Código"].get()
            producto = self._producto_desde_formulario()
            if not self.servicio.actualizar_producto(
                codigo,
                producto.nombre,
                producto.categoria,
                producto.precio,
                producto.stock,
            ):
                raise ValueError("No existe un producto con ese código.")
            self.guardar_datos()
            self._actualizar_tablas()
            self.producto_estado.set(f"Producto {codigo.strip()} actualizado correctamente.")
        except (ValueError, TypeError) as error:
            messagebox.showerror("Producto inválido", str(error))

    def _producto_desde_formulario(self) -> Producto:
        return Producto(
            self.producto_vars["Código"].get(),
            self.producto_vars["Nombre"].get(),
            self.producto_vars["Categoría"].get(),
            float(self.producto_vars["Precio"].get()),
            int(self.producto_vars["Stock"].get()),
        )

    def _mostrar_producto(self, producto: Producto) -> None:
        valores = {
            "Código": producto.codigo,
            "Nombre": producto.nombre,
            "Categoría": producto.categoria,
            "Precio": str(producto.precio),
            "Stock": str(producto.stock),
        }
        for campo, valor in valores.items():
            self.producto_vars[campo].set(valor)

    def _limpiar_producto(self) -> None:
        self._limpiar(self.producto_vars)
        self.producto_estado.set("Formulario listo para un nuevo producto.")

    def _eliminar_producto(self) -> None:
        seleccion = self.productos_tree.selection()
        if not seleccion:
            return
        codigo = self.productos_tree.item(seleccion[0], "values")[0]
        if self.servicio.eliminar_producto(codigo):
            self.guardar_datos()
            self._actualizar_tablas()
            self._limpiar_producto()
            self.producto_estado.set(f"Producto {codigo} eliminado correctamente.")

    def _actualizar_total_estimado(self) -> None:
        codigo = self._productos_venta.get(self.venta_producto.get())
        producto = self.servicio.buscar_producto(codigo or "")
        try:
            cantidad = int(self.venta_cantidad.get())
        except ValueError:
            cantidad = 0
        total = producto.precio * cantidad if producto is not None and cantidad > 0 else 0
        self.venta_total.set(f"Total estimado: ${total:.2f}")

    def _registrar_venta(self) -> None:
        usuario_identificacion = self._usuarios_venta.get(self.venta_usuario.get(), "")
        producto_codigo = self._productos_venta.get(self.venta_producto.get(), "")
        try:
            cantidad = int(self.venta_cantidad.get())
            venta = self.servicio.registrar_venta(
                usuario_identificacion,
                producto_codigo,
                cantidad,
            )
            self.guardar_datos()
            self._actualizar_tablas()
            self.venta_cantidad.set("1")
            self.venta_estado.set(
                f"Venta {venta.codigo} registrada. Total: ${venta.total:.2f}."
            )
            self._actualizar_total_estimado()
        except (ValueError, TypeError) as error:
            messagebox.showerror("No se pudo registrar la venta", str(error))

    def _actualizar_tablas(self) -> None:
        for tabla in (
            getattr(self, "productos_tree", None),
            getattr(self, "usuarios_tree", None),
            getattr(self, "ventas_tree", None),
        ):
            if tabla is not None:
                tabla.delete(*tabla.get_children())
        for producto in self.servicio.listar_productos():
            self.productos_tree.insert("", "end", values=(producto.codigo, producto.nombre, producto.categoria, f"{producto.precio:.2f}", producto.stock))
        for usuario in self.servicio.listar_usuarios():
            self.usuarios_tree.insert(
                "",
                "end",
                values=(
                    usuario.identificacion,
                    usuario.nombre,
                    usuario.correo,
                    usuario.nombre_usuario,
                ),
            )
        if hasattr(self, "ventas_tree"):
            for venta in self.servicio.listar_ventas():
                self.ventas_tree.insert(
                    "",
                    "end",
                    values=(
                        venta.codigo,
                        venta.fecha,
                        venta.nombre_usuario,
                        venta.producto_nombre,
                        venta.cantidad,
                        f"${venta.precio_unitario:.2f}",
                        f"${venta.total:.2f}",
                    ),
                )
        if hasattr(self, "venta_usuario_combo"):
            self._usuarios_venta = {
                f"{usuario.nombre} - {usuario.identificacion}": usuario.identificacion
                for usuario in self.servicio.listar_usuarios()
            }
            self._productos_venta = {
                f"{producto.nombre} - {producto.codigo} | ${producto.precio:.2f} | stock {producto.stock}": producto.codigo
                for producto in self.servicio.listar_productos()
            }
            self.venta_usuario_combo["values"] = tuple(self._usuarios_venta)
            self.venta_producto_combo["values"] = tuple(self._productos_venta)
            self._actualizar_total_estimado()

    @staticmethod
    def _limpiar(variables: dict[str, tk.StringVar]) -> None:
        for variable in variables.values():
            variable.set("")
