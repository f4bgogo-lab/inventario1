# -*- coding: utf-8 -*-
"""
Módulo: reportes.py
Descripción: Funciones analíticas y de reporte para el sistema de inventario y ventas.
"""

CATEGORIAS_VALIDAS = [
    "Laptops", "Monitores", "Periféricos", "Audio",
    "Almacenamiento", "Componentes", "Impresión", "Redes"
]

def calcular_total_unidades_vendidas(ventas: list) -> int:
    if not ventas: return 0
    return sum(v.get("cantidad", 0) for v in ventas)

def calcular_ingresos_totales(ventas: list) -> float:
    if not ventas: return 0.0
    return sum(v.get("cantidad", 0) * v.get("precio_unitario", 0.0) for v in ventas)

def _obtener_cantidades_por_producto(ventas: list) -> dict:
    conteo = {}
    for v in ventas:
        id_prod = v.get("id_producto")
        if id_prod:
            conteo[id_prod] = conteo.get(id_prod, 0) + v.get("cantidad", 0)
    return conteo

def obtener_productos_mas_vendidos(ventas: list, top: int = 5) -> list:
    if not ventas or top <= 0: return []
    conteo = _obtener_cantidades_por_producto(ventas)
    ordenados = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    return ordenados[:top]

def obtener_productos_menos_vendidos(ventas: list, top: int = 5) -> list:
    if not ventas or top <= 0: return []
    conteo = _obtener_cantidades_por_producto(ventas)
    ordenados = sorted(conteo.items(), key=lambda x: x[1], reverse=False)
    return ordenados[:top]

def obtener_productos_stock_bajo(inventario: list) -> list:
    if not inventario: return []
    return [p for p in inventario if p.get("stock", 0) <= p.get("stock_minimo", 0)]

def calcular_valor_inventario(inventario: list, en_base_a_costo: bool = True) -> float:
    if not inventario: return 0.0
    llave_precio = "precio_costo" if en_base_a_costo else "precio_venta"
    return sum(p.get("stock", 0) * p.get(llave_precio, 0.0) for p in inventario)

def generar_ventas_por_categoria(ventas: list, inventario: list) -> dict:
    reporte_cat = {cat: 0.0 for cat in CATEGORIAS_VALIDAS}
    if not ventas or not inventario: return reporte_cat
    mapa_categorias = {p["id"]: p["categoria"] for p in inventario if "id" in p and "categoria" in p}
    for v in ventas:
        id_prod = v.get("id_producto")
        cat_producto = mapa_categorias.get(id_prod)
        if cat_producto in reporte_cat:
            reporte_cat[cat_producto] += v.get("cantidad", 0) * v.get("precio_unitario", 0.0)
    return reporte_cat

def identificar_requerimiento_reabastecimiento(inventario: list) -> list:
    productos_bajos = obtener_productos_stock_bajo(inventario)
    resultado = []
    for p in productos_bajos:
        cantidad_sugerida = (p.get("stock_minimo", 0) * 2) - p.get("stock", 0)
        resultado.append({
            "id": p.get("id"),
            "nombre": p.get("nombre"),
            "stock_actual": p.get("stock"),
            "sugerencia_compra": max(cantidad_sugerida, 1)
        })
    return resultado

def generar_reporte_general(ventas: list, inventario: list) -> dict:
    ingresos = calcular_ingresos_totales(ventas)
    mapa_costos = {p["id"]: p["precio_costo"] for p in inventario if "id" in p}
    costo_total_vendido = sum(v.get("cantidad", 0) * mapa_costos.get(v.get("id_producto"), 0.0) for v in ventas)
    return {
        "total_unidades_vendidas": calcular_total_unidades_vendidas(ventas),
        "ingresos_totales": ingresos,
        "ganancia_estimada": ingresos - costo_total_vendido,
        "valor_inventario_costo": calcular_valor_inventario(inventario, en_base_a_costo=True),
        "productos_criticos_stock": len(obtener_productos_stock_bajo(inventario)),
        "top_producto_estrella": obtener_productos_mas_vendidos(ventas, top=1)
    }
