# ==============================================
# SESIÓN: ILUSTRACIÓN DE MÉTRICAS DE SIMILITUD
# Ejemplo con tres productos de ahorro / inversión
# ==============================================

# ----------------------------------------------
# 1. Importar bibliotecas necesarias
# ----------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import norm
from pathlib import Path
from mpl_toolkits.mplot3d import Axes3D  # necesario para el gráfico 3D

# ----------------------------------------------
# 2. Definir los vectores de ejemplo
# ----------------------------------------------
# Dimensiones (todas entre 0 y 1):
# [Liquidez y simplicidad, Seguridad del capital, Enfoque agresivo de crecimiento]

# A: Cuenta de ahorro digital
# - Muy líquida y fácil de usar
# - Muy segura
# - Casi nada agresiva
A = np.array([1.0, 0.9, 0.3])

# B: Depósito a plazo fijo
# - Menos líquido que la cuenta de ahorro (hay que esperar al vencimiento)
# - Igual de seguro (garantizado por el banco)
# - Un poco más orientado a rendimiento que la cuenta de ahorro
B = np.array([0.8, 1.0, 0.4])

# C: Fondo de inversión agresivo
# - Mucho menos líquido
# - Menos seguro (alta volatilidad)
# - Muy agresivo en búsqueda de rentabilidad
C = np.array([0.3, 0.4, 1.1])

# ----------------------------------------------
# Visualización 3D mejorada
# ----------------------------------------------
fig = plt.figure(figsize=(9, 8))
ax = fig.add_subplot(111, projection='3d')

# 🎨 Colores diferenciados y grosor equilibrado
ax.quiver(0, 0, 0, *A, color='#1f77b4', linewidth=3, arrow_length_ratio=0.1,
          label='Cuenta de ahorro digital')
ax.quiver(0, 0, 0, *B, color='#2ca02c', linewidth=3, arrow_length_ratio=0.1,
          label='Depósito a plazo fijo')
ax.quiver(0, 0, 0, *C, color='#ff7f0e', linewidth=3, arrow_length_ratio=0.1,
          label='Fondo de inversión agresivo')

# Límites y etiquetas con mayor visibilidad
ax.set_xlim([0, 1.1])
ax.set_ylim([0, 1.1])
ax.set_zlim([0, 1.1])
ax.set_xlabel('Liquidez / Simplicidad', fontsize=12, labelpad=12)
ax.set_ylabel('Seguridad del capital', fontsize=12, labelpad=12)
ax.set_zlabel('Enfoque agresivo / Crecimiento', fontsize=12, labelpad=15)

# Relación de aspecto más alta (para que se note el eje Z)
ax.set_box_aspect([1, 1, 1.2])

# Cámara: ángulo más natural
ax.view_init(elev=22, azim=40)

# Grid fino y fondo gris claro para contraste
ax.xaxis.pane.fill = True
ax.yaxis.pane.fill = True
ax.zaxis.pane.fill = True
ax.xaxis.pane.set_facecolor((0.95, 0.95, 0.95, 1.0))
ax.yaxis.pane.set_facecolor((0.95, 0.95, 0.95, 1.0))
ax.zaxis.pane.set_facecolor((0.98, 0.98, 0.98, 1.0))
ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

# Título y leyenda en mejor posición
ax.set_title('Productos de inversión como vectores en 3D', fontsize=14, pad=15)
ax.legend(loc='upper left', fontsize=10, frameon=True, edgecolor='gray')

fig.subplots_adjust(left=0.02, right=0.98, bottom=0.16, top=0.92)
output_path = Path(__file__).with_name("productos_bancarios_3d.png")
plt.savefig(output_path, dpi=250, bbox_inches="tight", pad_inches=0.35)
plt.close(fig)

# --------------------------------------------
# 4️⃣ Calcular las tres métricas de similitud
# --------------------------------------------
# 4.1. Similitud del Coseno (Cosine Similarity)
# Mide el ángulo entre dos vectores (proximidad de dirección)
cos_AB = np.dot(A, B) / (norm(A) * norm(B))
cos_AC = np.dot(A, C) / (norm(A) * norm(C))
cos_BC = np.dot(B, C) / (norm(B) * norm(C))

# --------------------------------------------
# Mostrar los resultados
# --------------------------------------------
print("========= RESULTADOS =========")
print("\n🔹 Similitud del Coseno")
print(f"A vs B: {cos_AB:.3f}")
print(f"A vs C: {cos_AC:.3f}")
print(f"B vs C: {cos_BC:.3f}")

# 4.2. Distancia Euclidiana (L2 Norm)
# Mide la distancia geométrica absoluta entre los puntos
l2_AB = norm(A - B)
l2_AC = norm(A - C)
l2_BC = norm(B - C)

# --------------------------------------------
# Mostrar los resultados
# --------------------------------------------
print("========= RESULTADOS =========")
print("\n🔹 Distancia Euclidiana (L2 Norm)")
print(f"A vs B: {l2_AB:.3f}")
print(f"A vs C: {l2_AC:.3f}")
print(f"B vs C: {l2_BC:.3f}")

# 4.3. Producto Interno (Dot Product)
# Mide la proyección de un vector sobre otro
dot_AB = np.dot(A, B)
dot_AC = np.dot(A, C)
dot_BC = np.dot(B, C)

# --------------------------------------------
# Mostrar los resultados
# --------------------------------------------
print("========= RESULTADOS =========")
print("\n🔹 Producto Interno (Dot Product)")
print(f"A vs B: {dot_AB:.3f}")
print(f"A vs C: {dot_AC:.3f}")
print(f"B vs C: {dot_BC:.3f}")
