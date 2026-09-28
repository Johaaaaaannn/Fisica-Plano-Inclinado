import pygame
import math
import sys


def pedir(mensaje, valor_defecto):
    while True:
        try:
            texto = input(f"{mensaje} [Enter = {valor_defecto}]: ").strip()
            return valor_defecto if texto == "" else float(texto)
        except ValueError:
            print("Numero invalido")


print("\nSIMULADOR FISICO - Dos masas conectadas\n")

m1 = pedir("m1 (masa derecha, kg)", 5.0)
m2 = pedir("m2 (masa izquierda, kg)", 3.0)
mu_s1 = pedir("mu_s1 (friccion estatica bajo m2)", 0.25)
mu_s2 = pedir("mu_s2 (friccion estatica bajo m1)", 0.25)
theta_deg = pedir("Angulo theta (grados)", 30.0)

mu_k1 = 0.80 * mu_s1
mu_k2 = 0.80 * mu_s2

pygame.init()

WIDTH, HEIGHT = 1200, 780
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador Fisico - Dos masas en planos inclinados")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 15)
font_b = pygame.font.SysFont("Arial", 18, bold=True)
font_title = pygame.font.SysFont("Arial", 23, bold=True)

BG = (248, 250, 255)
BLACK = (15, 15, 20)
GRAY = (90, 90, 100)
RED = (220, 60, 60)
BLUE = (40, 100, 210)
GREEN = (30, 160, 70)
ORANGE = (230, 140, 20)
WHITE = (255, 255, 255)
LIGHT = (230, 235, 245)

G = 9.81
RAMP_LENGTH_M = 8.0
BOX = 74


def calcular_fisica(m1, m2, mu_s1, mu_s2, mu_k1, mu_k2, theta, v):
    """
    v > 0: m1 baja por la derecha y m2 sube.
    v < 0: m2 baja por la izquierda y m1 sube.
    """
    seno = math.sin(theta)
    coseno = math.cos(theta)

    fuerza_gravedad = (m1 - m2) * G * seno
    friccion_estatica_max = (mu_s2 * m1 + mu_s1 * m2) * G * coseno

    if abs(v) < 1e-5 and abs(fuerza_gravedad) <= friccion_estatica_max:
        return 0.0, "EQUILIBRIO ESTATICO"

    if abs(v) >= 1e-5:
        direccion = math.copysign(1.0, v)
    else:
        direccion = math.copysign(1.0, fuerza_gravedad)

    friccion_cinetica = (mu_k2 * m1 + mu_k1 * m2) * G * coseno
    fuerza_neta = fuerza_gravedad - direccion * friccion_cinetica
    aceleracion = fuerza_neta / (m1 + m2)

    if direccion > 0:
        estado = "m1 BAJA y jala m2 ARRIBA"
    else:
        estado = "m2 BAJA y jala m1 ARRIBA"

    return aceleracion, estado


cx = WIDTH // 2
cy = HEIGHT // 2 + 90
base_half = 380


def actualizar_geometria(theta):
    altura = base_half * math.tan(theta)
    top = (cx, cy - altura)
    left = (cx - base_half, cy)
    right = (cx + base_half, cy)
    return top, left, right


def posicion_bloque(s_metros, izquierda, top, left, right, theta):
    fraccion = max(0.08, min(0.88, s_metros / RAMP_LENGTH_M))

    if izquierda:
        fraccion_izquierda = 1.0 - fraccion
        x = top[0] + (left[0] - top[0]) * fraccion_izquierda
        y = top[1] + (left[1] - top[1]) * fraccion_izquierda
        angulo = math.pi - theta
    else:
        x = top[0] + (right[0] - top[0]) * fraccion
        y = top[1] + (right[1] - top[1]) * fraccion
        angulo = theta

    return x, y, angulo


theta = math.radians(theta_deg)
top, left, right = actualizar_geometria(theta)

s = RAMP_LENGTH_M * 0.40
v = 0.0
paused = False
running = True

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                s = RAMP_LENGTH_M * 0.40
                v = 0.0
            elif event.key == pygame.K_UP:
                m1 = min(30.0, m1 + 0.3)
            elif event.key == pygame.K_DOWN:
                m1 = max(0.2, m1 - 0.3)
            elif event.key == pygame.K_RIGHT:
                m2 = min(30.0, m2 + 0.3)
            elif event.key == pygame.K_LEFT:
                m2 = max(0.2, m2 - 0.3)
            elif event.key == pygame.K_w:
                mu_s1 = min(1.2, mu_s1 + 0.04)
                mu_k1 = 0.80 * mu_s1
            elif event.key == pygame.K_s:
                mu_s1 = max(0.0, mu_s1 - 0.04)
                mu_k1 = 0.80 * mu_s1
            elif event.key == pygame.K_d:
                mu_s2 = min(1.2, mu_s2 + 0.04)
                mu_k2 = 0.80 * mu_s2
            elif event.key == pygame.K_a:
                mu_s2 = max(0.0, mu_s2 - 0.04)
                mu_k2 = 0.80 * mu_s2
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                theta_deg = min(45.0, theta_deg + 1.0)
                theta = math.radians(theta_deg)
                top, left, right = actualizar_geometria(theta)
            elif event.key == pygame.K_MINUS:
                theta_deg = max(12.0, theta_deg - 1.0)
                theta = math.radians(theta_deg)
                top, left, right = actualizar_geometria(theta)

    a, estado = calcular_fisica(
        m1, m2, mu_s1, mu_s2, mu_k1, mu_k2, theta, v
    )

    if not paused:
        v_anterior = v
        v += a * dt
        s += v * dt

        if v_anterior * v < 0:
            v = 0.0

        s_min = RAMP_LENGTH_M * 0.10
        s_max = RAMP_LENGTH_M * 0.85

        if s < s_min:
            s = s_min
            v = 0.0
        elif s > s_max:
            s = s_max
            v = 0.0

    x1, y1, ang1 = posicion_bloque(s, False, top, left, right, theta)
    x2, y2, ang2 = posicion_bloque(s, True, top, left, right, theta)

    # Eleva los bloques para que su cara inferior descanse sobre la rampa.
    apoyo = BOX / 2
    x1 += apoyo * math.sin(theta)
    y1 -= apoyo * math.cos(theta)
    x2 -= apoyo * math.sin(theta)
    y2 -= apoyo * math.cos(theta)

    screen.fill(BG)

    pygame.draw.line(
        screen, (160, 160, 170),
        (40, cy + 6), (WIDTH - 40, cy + 6), 4
    )

    pygame.draw.polygon(screen, LIGHT, [top, left, right])
    pygame.draw.lines(screen, BLACK, True, [top, left, right], 5)

    pygame.draw.circle(
        screen, (50, 50, 55),
        (int(top[0]), int(top[1]) - 10), 16
    )
    pygame.draw.circle(
        screen, (190, 190, 195),
        (int(top[0]), int(top[1]) - 10), 9
    )

    pygame.draw.line(
        screen, (30, 30, 35), (x2, y2), (top[0], top[1] - 6), 4
    )
    pygame.draw.line(
        screen, (30, 30, 35), (x1, y1), (top[0], top[1] - 6), 4
    )

    bloque_azul = pygame.Surface((BOX, BOX), pygame.SRCALPHA)
    pygame.draw.rect(bloque_azul, BLUE, (0, 0, BOX, BOX), border_radius=8)
    pygame.draw.rect(
        bloque_azul, (20, 50, 140), (0, 0, BOX, BOX),
        3, border_radius=8
    )
    azul_rotado = pygame.transform.rotate(
        bloque_azul, math.degrees(ang2) - 90
    )
    screen.blit(azul_rotado, azul_rotado.get_rect(center=(x2, y2)))
    screen.blit(
        font_b.render(f"m2={m2:.1f}", True, WHITE), (x2 - 28, y2 - 9)
    )

    bloque_rojo = pygame.Surface((BOX, BOX), pygame.SRCALPHA)
    pygame.draw.rect(bloque_rojo, RED, (0, 0, BOX, BOX), border_radius=8)
    pygame.draw.rect(
        bloque_rojo, (150, 25, 25), (0, 0, BOX, BOX),
        3, border_radius=8
    )
    rojo_rotado = pygame.transform.rotate(
        bloque_rojo, -math.degrees(ang1) + 90
    )
    screen.blit(rojo_rotado, rojo_rotado.get_rect(center=(x1, y1)))
    screen.blit(
        font_b.render(f"m1={m1:.1f}", True, WHITE), (x1 - 28, y1 - 9)
    )

    pygame.draw.arc(
        screen, ORANGE, (left[0] - 45, cy - 45, 90, 90), 0, theta, 3
    )
    pygame.draw.arc(
        screen, ORANGE, (right[0] - 45, cy - 45, 90, 90),
        math.pi - theta, math.pi, 3
    )

    texto_theta = font.render(
        f"theta={theta_deg:.0f} grados", True, ORANGE
    )
    screen.blit(texto_theta, (left[0] + 15, cy - 60))
    screen.blit(texto_theta, (right[0] - 110, cy - 60))

    # Panel compacto de parametros.
    pygame.draw.rect(screen, WHITE, (12, 12, 335, 292), border_radius=12)
    pygame.draw.rect(
        screen, (120, 120, 130), (12, 12, 335, 292),
        2, border_radius=12
    )
    screen.blit(font_title.render("Parametros", True, BLACK), (28, 22))

    lineas = [
        f"m1 (derecha)   = {m1:5.2f} kg",
        f"m2 (izquierda) = {m2:5.2f} kg",
        f"mu_s1 bajo m2  = {mu_s1:5.2f}",
        f"mu_s2 bajo m1  = {mu_s2:5.2f}",
        f"mu_k1 / mu_k2  = {mu_k1:4.2f} / {mu_k2:4.2f}",
        f"theta          = {theta_deg:5.1f} grados",
        "",
        f"Aceleracion    = {a:7.3f} m/s2",
        f"Velocidad      = {v:7.3f} m/s",
    ]

    y = 60
    for linea in lineas:
        color = GREEN if "Aceleracion" in linea and abs(a) < 1e-5 else BLACK
        screen.blit(font.render(linea, True, color), (28, y))
        y += 21

    color_estado = GREEN if "EQUILIBRIO" in estado else (RED if v >= 0 else BLUE)
    screen.blit(font_b.render(estado, True, color_estado), (28, y + 8))

    # Panel de controles.
    pygame.draw.rect(
        screen, WHITE, (WIDTH - 330, 12, 315, 250), border_radius=12
    )
    pygame.draw.rect(
        screen, (120, 120, 130), (WIDTH - 330, 12, 315, 250),
        2, border_radius=12
    )
    screen.blit(font_title.render("Controles", True, BLACK), (WIDTH - 310, 22))

    controles = [
        "UP / DOWN       m1  +/- 0.3",
        "RIGHT / LEFT    m2  +/- 0.3",
        "W / S           mu_s1 +/- 0.04",
        "D / A           mu_s2 +/- 0.04",
        "+ / -           theta +/- 1 grado",
        "R               Reiniciar",
        "ESPACIO         Pausar",
        "ESC             Salir",
    ]

    y = 65
    for control in controles:
        screen.blit(font.render(control, True, BLACK), (WIDTH - 310, y))
        y += 22

    if paused:
        screen.blit(
            font_b.render("PAUSADO", True, ORANGE), (WIDTH // 2 - 55, 25)
        )

    leyenda = "Rojo = m1 derecha     Azul = m2 izquierda     a > 0: m1 baja"
    screen.blit(
        font.render(leyenda, True, GRAY), (WIDTH // 2 - 280, HEIGHT - 35)
    )

    pygame.display.flip()

pygame.quit()
sys.exit()