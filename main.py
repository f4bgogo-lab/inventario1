# -*- coding: utf-8 -*-
"""
Módulo: main.py
Descripción: Menú interactivo centralizado por consola para el sistema de inventario y ventas.
"""
import json
import os
from datetime import datetime

# Importar los módulos analíticos y de alertas
import modulos.reportes as reportes
import modulos.alertas as alertas
import modulos.stock as stock
import modulos.ventas as ventas_modulo

PRODUCTOS_PATH = "datos/productos.json"
VENTAS_PATH = "datos/ventas.json"

def cargar_datos(ruta):
    """Carga datos desde una ruta JSON especificada."""
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f" [ERROR] No se pudo leer {ruta}: {e}")
        return []

def guardar_datos(datos, ruta):
    """Guarda los datos en formato JSON formateado."""
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f" [ERROR] No se pudo guardar en {ruta}: {e}")
        return False

def mostrar_submenu_reportes():
    """Muestra el submenú de reportes analíticos."""
    while True:
        print("\n" + "=" * 60)
        print("  SISTEMA DE REPORTES ANALÍTICOS ".center(60, "📊"))
        print("=" * 60)
        print(" 1. 📈 Resumen Ejecutivo")
        print(" 2. 🗂️  Ventas por Categoría")
        print(" 3. ⚠️  Productos Críticos (Sugerencia de Reabastecimiento)")
        print(" 4. ↩️  Volver al Menú Principal")
        print("-" * 60)
        
        opcion = input("Seleccione una opción de reporte (1-4): ").strip()
        
        # Cargar datos actualizados antes de cada reporte
        inventario = cargar_datos(PRODUCTOS_PATH)
        ventas = cargar_datos(VENTAS_PATH)
        
        if opcion == "1":
            resumen = reportes.generar_reporte_general(ventas, inventario)
            print("\n" + "■" * 60)
            print("  RESUMEN EJECUTIVO DE OPERACIONES ".center(60))
            print("■" * 60)
            print(f" • Total Unidades Vendidas : {resumen['total_unidades_vendidas']}")
            print(f" • Ingresos Totales        : ${resumen['ingresos_totales']:,.2f}")
            print(f" • Ganancia Estimada       : ${resumen['ganancia_estimada']:,.2f}")
            print(f" • Valor de Inventario     : ${resumen['valor_inventario_costo']:,.2f} (a costo)")
            print(f" • Ítems en Stock Crítico   : {resumen['productos_criticos_stock']}")
            
            top_prod = resumen['top_producto_estrella']
            if top_prod:
                id_p, cant = top_prod[0]
                # Buscar nombre de producto
                nombre = next((p.get("nombre", "Desconocido") for p in inventario if p.get("id") == id_p), "Desconocido")
                print(f" • Producto Estrella       : {nombre} ({cant} unds)")
            else:
                print(" • Producto Estrella       : N/A")
            print("■" * 60 + "\n")
            
        elif opcion == "2":
            reporte_cat = reportes.generar_ventas_por_categoria(ventas, inventario)
            print("\n" + "■" * 60)
            print("  DISTRIBUCIÓN DE VENTAS POR CATEGORÍA ".center(60))
            print("■" * 60)
            for cat, total in reporte_cat.items():
                barra = "█" * int(min(total / 500, 20))
                print(f" • {cat:<15} : ${total:<10,.2f} {barra}")
            print("■" * 60 + "\n")
            
        elif opcion == "3":
            reabastecimiento = reportes.identificar_requerimiento_reabastecimiento(inventario)
            print("\n" + "■" * 60)
            print("  REQUERIMIENTO DE REABASTECIMIENTO DE STOCK ".center(60))
            print("■" * 60)
            if not reabastecimiento:
                print(">>> No hay requerimientos de reabastecimiento activos. <<<".center(60))
            else:
                print(f"{'ID':<10} | {'PRODUCTO':<30} | {'ACTUAL':<8} | {'SUGERENCIA':<10}")
                print("-" * 60)
                for item in reabastecimiento:
                    nombre_truncado = item['nombre'][:28] + ".." if len(item['nombre']) > 30 else item['nombre']
                    print(f"{item['id']:<10} | {nombre_truncado:<30} | {item['stock_actual']:<8} | {item['sugerencia_compra']:<10}")
            print("■" * 60 + "\n")
            
        elif opcion == "4":
            print("\nRetornando al menú principal...")
            break
        else:
            print("\n [ERROR] Opción no válida. Ingrese un número entre 1 y 4.")

def simular_venta():
    """Función interactiva para registrar una venta y actualizar el inventario."""
    print("\n" + "•" * 60)
    print("  SIMULADOR DE TRANSACCIONES / REGISTRO DE VENTAS ".center(60))
    print("•" * 60)
    
    inventario = cargar_datos(PRODUCTOS_PATH)
    if not inventario:
        print(" [ERROR] El inventario está vacío o no existe. No se puede realizar ventas.")
        return

    # Mostrar catálogo resumido para comodidad del usuario
    print(f"{'ID':<10} | {'PRODUCTO':<35} | {'PRECIO':<10} | {'STOCK':<5}")
    print("-" * 60)
    for p in inventario:
        nombre_trunc = p.get('nombre', '')[:33] + '..' if len(p.get('nombre', '')) > 35 else p.get('nombre', '')
        print(f"{p.get('id', ''):<10} | {nombre_trunc:<35} | ${p.get('precio_venta', 0.0):<10,.2f} | {p.get('stock', 0):<5}")
    print("-" * 60)

    id_prod = input("\nIngrese el ID del producto que desea vender: ").strip().upper()
    
    # Buscar producto
    producto = stock.buscar_producto_por_id(inventario, id_prod)
    if not producto:
        print(f"\n ❌ [ERROR] El producto con ID '{id_prod}' no fue encontrado en la base de datos.")
        return

    try:
        cantidad_solicitada = int(input(f"Ingrese la cantidad a vender (Stock actual: {producto['stock']}): "))
    except ValueError:
        print("\n ❌ [ERROR] La cantidad ingresada debe ser un número entero válido.")
        return

    # Invocar a la lógica pura de ventas
    exito, datos_o_error, inventario_actualizado = ventas_modulo.procesar_logica_venta(
        inventario, id_prod, cantidad_solicitada
    )

    if exito:
        ventas = cargar_datos(VENTAS_PATH)
        id_venta_autoincremental = len(ventas) + 1
        nueva_venta_id = f"SALE-{id_venta_autoincremental:03d}"
        
        # Diccionario estructurado de la transacción
        nueva_venta = {
            "id": nueva_venta_id,
            "id_venta": id_venta_autoincremental,
            "id_producto": datos_o_error["id_producto"],
            "cantidad": datos_o_error["cantidad"],
            "precio_unitario": datos_o_error["precio_unitario"],
            "total": datos_o_error["total"],
            "fecha": datetime.now().strftime("%Y-%m-%d")
        }
        ventas.append(nueva_venta)
        
        # Persistir cambios
        if guardar_datos(inventario_actualizado, PRODUCTOS_PATH) and guardar_datos(ventas, VENTAS_PATH):
            print(f"\n ✅ [TRANSACCIÓN EXITOSA] Se vendieron {cantidad_solicitada} unidades de '{producto['nombre']}'.")
            print(f" Registro creado: {nueva_venta_id} por ${datos_o_error['total']:,.2f}")
            print(f" Total Cobrado: ${datos_o_error['total']:,.2f}")
            
            # Invocar la auditoría de alertas en tiempo real
            print("\n[INFO] Ejecutando auditoría de inventario post-venta...")
            alertas.verificar_y_notificar(PRODUCTOS_PATH)
        else:
            print("\n ❌ [ERROR-SYS] Ocurrió un error al persistir los cambios en la base de datos.")
    else:
        print(f"\n ❌ {datos_o_error}")

def reabastecer_almacen():
    """Función interactiva para reabastecer el stock de un producto."""
    print("\n" + "•" * 60)
    print("  MÓDULO DE STOCK / REABASTECIMIENTO DE ALMACÉN ".center(60))
    print("•" * 60)
    
    inventario = cargar_datos(PRODUCTOS_PATH)
    if not inventario:
        print(" [ERROR] El inventario está vacío o no existe.")
        return

    # Mostrar catálogo resumido
    print(f"{'ID':<10} | {'PRODUCTO':<35} | {'STOCK':<5} | {'STOCK MÍN.':<10}")
    print("-" * 60)
    for p in inventario:
        nombre_trunc = p.get('nombre', '')[:33] + '..' if len(p.get('nombre', '')) > 35 else p.get('nombre', '')
        print(f"{p.get('id', ''):<10} | {nombre_trunc:<35} | {p.get('stock', 0):<5} | {p.get('stock_minimo', 0):<10}")
    print("-" * 60)

    id_prod = input("\nIngrese el ID del producto a reabastecer: ").strip().upper()
    
    # Buscar producto para validar antes de pedir cantidad
    producto = stock.buscar_producto_por_id(inventario, id_prod)
    if not producto:
        print(f"\n ❌ [ERROR] El producto con ID '{id_prod}' no fue encontrado en la base de datos.")
        return

    try:
        cantidad_ingreso = int(input(f"Ingrese la cantidad de unidades que ingresan (Stock actual: {producto['stock']}): "))
    except ValueError:
        print("\n ❌ [ERROR] La cantidad ingresada debe ser un número entero válido.")
        return

    # Invocar la función de stock
    exito, mensaje, inventario_actualizado = stock.modificar_existencias(
        inventario, id_prod, cantidad_ingreso, es_ingreso=True
    )

    if exito:
        if guardar_datos(inventario_actualizado, PRODUCTOS_PATH):
            print(f"\n ✅ [INGRESO EXITOSO] {mensaje}")
            print("\n[INFO] Ejecutando auditoría de inventario post-reabastecimiento...")
            alertas.verificar_y_notificar(PRODUCTOS_PATH)
        else:
            print("\n ❌ [ERROR-SYS] Ocurrió un error al persistir los cambios.")
    else:
        print(f"\n ❌ [ERROR] {mensaje}")

def despachar_venta():
    """Función interactiva para procesar el despacho de una venta confirmada."""
    print("\n" + "•" * 60)
    print("  MÓDULO DE STOCK / DESPACHO POR VENTA CONFIRMADA ".center(60))
    print("•" * 60)
    
    inventario = cargar_datos(PRODUCTOS_PATH)
    if not inventario:
        print(" [ERROR] El inventario está vacío o no existe.")
        return

    # Mostrar catálogo resumido
    print(f"{'ID':<10} | {'PRODUCTO':<35} | {'STOCK':<5} | {'STOCK MÍN.':<10}")
    print("-" * 60)
    for p in inventario:
        nombre_trunc = p.get('nombre', '')[:33] + '..' if len(p.get('nombre', '')) > 35 else p.get('nombre', '')
        print(f"{p.get('id', ''):<10} | {nombre_trunc:<35} | {p.get('stock', 0):<5} | {p.get('stock_minimo', 0):<10}")
    print("-" * 60)

    id_prod = input("\nIngrese el ID del producto a despachar: ").strip().upper()
    
    # Buscar producto para validar
    producto = stock.buscar_producto_por_id(inventario, id_prod)
    if not producto:
        print(f"\n ❌ [ERROR] El producto con ID '{id_prod}' no fue encontrado en la base de datos.")
        return

    try:
        cantidad_despacho = int(input(f"Ingrese la cantidad a vender/retirar (Stock actual: {producto['stock']}): "))
    except ValueError:
        print("\n ❌ [ERROR] La cantidad ingresada debe ser un número entero válido.")
        return

    # Invocar a la lógica pura de ventas
    exito, datos_o_error, inventario_actualizado = ventas_modulo.procesar_logica_venta(
        inventario, id_prod, cantidad_despacho
    )

    if exito:
        ventas = cargar_datos(VENTAS_PATH)
        id_venta_autoincremental = len(ventas) + 1
        nueva_venta_id = f"SALE-{id_venta_autoincremental:03d}"
        
        # Diccionario estructurado de la transacción
        nueva_venta = {
            "id": nueva_venta_id,
            "id_venta": id_venta_autoincremental,
            "id_producto": datos_o_error["id_producto"],
            "cantidad": datos_o_error["cantidad"],
            "precio_unitario": datos_o_error["precio_unitario"],
            "total": datos_o_error["total"],
            "fecha": datetime.now().strftime("%Y-%m-%d")
        }
        ventas.append(nueva_venta)
        
        # Persistir cambios
        if guardar_datos(inventario_actualizado, PRODUCTOS_PATH) and guardar_datos(ventas, VENTAS_PATH):
            print(f"\n ✅ [DESPACHO EXITOSO] Se retiraron {cantidad_despacho} unidades de '{producto['nombre']}'. Total: ${datos_o_error['total']:,.2f}")
            print("\n[INFO] Ejecutando auditoría de inventario post-despacho...")
            alertas.verificar_y_notificar(PRODUCTOS_PATH)
        else:
            print("\n ❌ [ERROR-SYS] Ocurrió un error al persistir los cambios.")
    else:
        print(f"\n ❌ {datos_o_error}")

def listar_historial_ventas():
    """Muestra el historial de ventas registradas de forma estética."""
    print("\n" + "•" * 80)
    print("  HISTORIAL DE VENTAS REGISTRADAS ".center(80))
    print("•" * 80)
    
    ventas = cargar_datos(VENTAS_PATH)
    inventario = cargar_datos(PRODUCTOS_PATH)
    
    if not ventas:
        print(">>> No hay registros de ventas en el historial. <<<".center(80))
        print("•" * 80 + "\n")
        return

    # Create a product name mapping for display
    mapa_nombres = {p.get("id"): p.get("nombre", "Desconocido") for p in inventario if "id" in p}
    
    print(f"{'ID VENTA':<10} | {'FECHA':<11} | {'PRODUCTO (ID)':<35} | {'CANT.':<6} | {'TOTAL':<12}")
    print("-" * 80)
    for v in ventas:
        id_v = v.get("id_venta") if "id_venta" in v else v.get("id", "")
        if isinstance(id_v, int):
            id_v_str = f"SALE-{id_v:03d}"
        else:
            id_v_str = str(id_v)
            
        fecha = v.get("fecha", "N/A")
        id_prod = v.get("id_producto", "N/A")
        nombre_prod = mapa_nombres.get(id_prod, "Desconocido")
        # truncate product name if too long
        nombre_trunc = nombre_prod[:22] + ".." if len(nombre_prod) > 24 else nombre_prod
        prod_display = f"{nombre_trunc} ({id_prod})"
        
        cant = v.get("cantidad", 0)
        total = v.get("total") if "total" in v else (cant * v.get("precio_unitario", 0.0))
        
        print(f"{id_v_str:<10} | {fecha:<11} | {prod_display:<35} | {cant:<6} | ${total:<11,.2f}")
    
    total_unidades = sum(v.get("cantidad", 0) for v in ventas)
    total_ingresos = sum(v.get("total", v.get("cantidad", 0) * v.get("precio_unitario", 0.0)) for v in ventas)
    print("-" * 80)
    print(f" TOTAL ACUMULADO: {len(ventas)} ventas | {total_unidades} unidades | ${total_ingresos:,.2f}".center(80))
    print("•" * 80 + "\n")

def main():
    """Menú principal del sistema de gestión."""
    while True:
        print("\n" + "=" * 60)
        print(" SISTEMA INTEGRADO DE INVENTARIO Y VENTAS ".center(60, "⚡"))
        print("=" * 60)
        print(" 1. 📊 Módulo de Reportes Analíticos")
        print(" 2. 🔍 Ejecutar Auditoría de Alertas (Stock Crítico)")
        print(" 3. 🛍️  Simular Venta de Producto")
        print(" 4. 📥 Reabastecimiento de Almacén")
        print(" 5. 📤 Despacho por Venta Confirmada")
        print(" 6. 📜 Listar Historial de Ventas")
        print(" 7. 🛑 Salir del Sistema")
        print("=" * 60)
        
        opcion = input("Seleccione una opción (1-7): ").strip()
        
        if opcion == "1":
            mostrar_submenu_reportes()
        elif opcion == "2":
            print("\n[INFO] Iniciando auditoría en tiempo real...")
            alertas.verificar_y_notificar(PRODUCTOS_PATH)
        elif opcion == "3":
            simular_venta()
        elif opcion == "4":
            reabastecer_almacen()
        elif opcion == "5":
            despachar_venta()
        elif opcion == "6":
            listar_historial_ventas()
        elif opcion == "7":
            print("\n" + "■" * 60)
            print(" ¡Muchas gracias por utilizar el Sistema de Importaciones! ".center(60))
            print(" Estado operacional finalizado exitosamente. ".center(60))
            print("■" * 60 + "\n")
            break
        else:
            print("\n [ERROR] Opción inválida. Ingrese una opción del 1 al 7.")

if __name__ == "__main__":
    main()
