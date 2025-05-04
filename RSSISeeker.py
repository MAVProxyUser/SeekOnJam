import pygame
import numpy as np
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("RSSI-Based Seeker Simulation")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)

# Adjustable cone direction variable
CONE_DIRECTION_OFFSET = 0  # You can set this to 180 if needed

# Seeker and Jammer properties
padding = 96
seeker = {'x': padding, 'y': padding, 'speed': 2, 'dragging': False, 'caught': False}
jammer = {
    'x': width - padding, 'y': height - padding, 'active': False,
    'dragging': False, 'random_walk': False, 'target_x': None, 'target_y': None,
    'signal_type': 'omni', 'signal_angle': 90, 'signal_length': np.sqrt(width**2 + height**2), 'rotation': 0
}
simulation_continues = True

def reset_simulation():
    global seeker, jammer, padding
    seeker = {'x': padding, 'y': padding, 'speed': 2, 'dragging': False, 'caught': False}
    jammer = {
        'x': width - padding, 'y': height - padding, 'active': False,
        'dragging': False, 'random_walk': False, 'target_x': None, 'target_y': None,
        'signal_type': 'omni', 'signal_angle': 90, 'signal_length': np.sqrt(width**2 + height**2), 'rotation': 0
    }

def is_point_in_cone(px, py, cx, cy, cone_angle, cone_length, cone_rotation):
    dx = px - cx
    dy = py - cy
    dist = np.sqrt(dx**2 + dy**2)

    if dist > cone_length:
        return False

    angle_to_point = (np.degrees(np.arctan2(dy, dx)) + 360) % 360
    cone_start = (cone_rotation - cone_angle / 2 + 360) % 360
    cone_end = (cone_rotation + cone_angle / 2 + 360) % 360

    if cone_start < cone_end:
        return cone_start <= angle_to_point <= cone_end
    else:
        return angle_to_point >= cone_start or angle_to_point <= cone_end

def move_seeker_towards_jammer(seeker, jammer):
    if not jammer['active']:
        return

    dx = jammer['x'] - seeker['x']
    dy = jammer['y'] - seeker['y']
    dist = np.sqrt(dx**2 + dy**2)

    if jammer['signal_type'] == 'omni' and dist <= jammer['signal_length']:
        if dist > 1:
            seeker['x'] += (dx / dist) * seeker['speed']
            seeker['y'] += (dy / dist) * seeker['speed']
        else:
            seeker['caught'] = True
    elif jammer['signal_type'] == 'cone':
        if is_point_in_cone(seeker['x'], seeker['y'], jammer['x'], jammer['y'], jammer['signal_angle'], jammer['signal_length'], jammer['rotation']):
            if dist > 1:
                seeker['x'] += (dx / dist) * seeker['speed']
                seeker['y'] += (dy / dist) * seeker['speed']
            else:
                seeker['caught'] = True

def move_jammer_randomly(jammer):
    if jammer['random_walk']:
        dx = jammer['target_x'] - jammer['x']
        dy = jammer['target_y'] - jammer['y']
        dist = np.sqrt(dx**2 + dy**2)
        if dist > 1:
            jammer['x'] += (dx / dist) * 2
            jammer['y'] += (dy / dist) * 2
        else:
            randomize_jammer_location(jammer, width, height)

def draw_signal(window, jammer):
    if jammer['signal_type'] == 'omni':
        pygame.draw.circle(window, GREEN, (int(jammer['x']), int(jammer['y'])), int(jammer['signal_length']), 1)
    else:
        jammer_rotation = (jammer['rotation'] + CONE_DIRECTION_OFFSET) % 360
        start_angle = np.deg2rad(jammer_rotation - jammer['signal_angle'] / 2)
        end_angle = np.deg2rad(jammer_rotation + jammer['signal_angle'] / 2)
        points = [
            (jammer['x'], jammer['y']),
            (jammer['x'] + jammer['signal_length'] * np.cos(start_angle), jammer['y'] + jammer['signal_length'] * np.sin(start_angle)),
            (jammer['x'] + jammer['signal_length'] * np.cos(end_angle), jammer['y'] + jammer['signal_length'] * np.sin(end_angle))
        ]
        pygame.draw.polygon(window, GREEN, points, 1)

def draw(window, seeker, jammer, simulation_continues):
    window.fill(BLACK)

    # Draw seeker
    pygame.draw.circle(window, RED, (int(seeker['x']), int(seeker['y'])), 10)

    # Draw jammer
    pygame.draw.circle(window, BLUE, (int(jammer['x']), int(jammer['y'])), 10)

    # Draw the signal representation
    draw_signal(window, jammer)

    # Interface elements
    font = pygame.font.Font(None, 36)

    # Draw "Jam" button
    pygame.draw.rect(window, GREEN if jammer['active'] else BLUE, (width - 140, 10, 100, 50))
    text = font.render("Jam" if not jammer['active'] else "Jamming", True, BLACK)
    window.blit(text, (width - 130, 20))

    # Draw signal type switch
    pygame.draw.rect(window, GREEN if jammer['signal_type'] == 'omni' else BLUE, (width - 140, 70, 100, 50))
    text = font.render("Omni" if jammer['signal_type'] == 'omni' else "Cone", True, BLACK)
    window.blit(text, (width - 130, 80))

    # Draw angle slider
    pygame.draw.rect(window, GRAY, (width - 140, 130, 100, 20))
    pygame.draw.rect(window, YELLOW, (width - 140, 130, jammer['signal_angle'], 20))
    angle_label = font.render("Angle", True, BLACK)
    window.blit(angle_label, (width - 140, 130))

    # Draw length slider
    pygame.draw.rect(window, GRAY, (width - 140, 190, 100, 20))
    pygame.draw.rect(window, YELLOW, (width - 140, 190, jammer['signal_length'] / (2 * np.sqrt(width**2 + height**2) / 200), 20))
    size_label = font.render("Size", True, BLACK)
    window.blit(size_label, (width - 140, 190))

    # Draw reset button
    pygame.draw.rect(window, WHITE, (width - 140, 250, 100, 50))
    text = font.render("Reset", True, BLACK)
    window.blit(text, (width - 130, 260))

    # Draw "Continue" checkbox
    pygame.draw.rect(window, WHITE, (width - 140, 310, 20, 20), 2)
    if simulation_continues:
        pygame.draw.line(window, WHITE, (width - 140, 310), (width - 120, 330), 2)
        pygame.draw.line(window, WHITE, (width - 140, 330), (width - 120, 310), 2)
    text = font.render("Cont.", True, WHITE)
    window.blit(text, (width - 110, 310))

    pygame.display.flip()

def main():
    global simulation_continues
    clock = pygame.time.Clock()

    dragging_angle = False
    dragging_length = False
    dragging_rotation = False

    reset_simulation()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if pygame.Rect(width - 140, 10, 100, 50).collidepoint(mouse_x, mouse_y):
                    jammer['active'] = not jammer['active']
                elif pygame.Rect(width - 140, 70, 100, 50).collidepoint(mouse_x, mouse_y):
                    jammer['signal_type'] = 'cone' if jammer['signal_type'] == 'omni' else 'omni'
                elif pygame.Rect(width - 140, 130, 100, 20).collidepoint(mouse_x, mouse_y):
                    dragging_angle = True
                elif pygame.Rect(width - 140, 190, 100, 20).collidepoint(mouse_x, mouse_y):
                    dragging_length = True
                elif pygame.Rect(width - 140, 250, 100, 50).collidepoint(mouse_x, mouse_y):
                    reset_simulation()
                elif pygame.Rect(width - 140, 310, 20, 20).collidepoint(mouse_x, mouse_y):
                    simulation_continues = not simulation_continues
                elif np.sqrt((mouse_x - seeker['x'])**2 + (mouse_y - seeker['y'])**2) < 10:
                    seeker['dragging'] = True
                elif np.sqrt((mouse_x - jammer['x'])**2 + (mouse_y - jammer['y'])**2) < 10:
                    jammer['dragging'] = True
                elif jammer['signal_type'] == 'cone' and np.sqrt((mouse_x - jammer['x'])**2 + (mouse_y - jammer['y'])**2) < jammer['signal_length']:
                    dragging_rotation = True

            elif event.type == pygame.MOUSEBUTTONUP:
                seeker['dragging'] = False
                jammer['dragging'] = False
                dragging_angle = False
                dragging_length = False
                dragging_rotation = False

            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                if seeker['dragging']:
                    seeker['x'], seeker['y'] = event.pos
                elif jammer['dragging']:
                    jammer['x'], jammer['y'] = event.pos
                elif dragging_angle:
                    mouse_x, _ = event.pos
                    jammer['signal_angle'] = max(0, min(100, mouse_x - (width - 140)))
                elif dragging_length:
                    mouse_x, _ = event.pos
                    jammer['signal_length'] = max(0, min(np.sqrt(width**2 + height**2), (mouse_x - (width - 140)) * (np.sqrt(width**2 + height**2) / 100)))
                elif dragging_rotation:
                    dx = mouse_x - jammer['x']
                    dy = mouse_y - jammer['y']
                    jammer['rotation'] = (np.degrees(np.arctan2(dy, dx)) + 360) % 360

        if not seeker['dragging'] and not (seeker['caught'] and not simulation_continues):
            move_seeker_towards_jammer(seeker, jammer)
        if not jammer['dragging']:
            move_jammer_randomly(jammer)

        draw(window, seeker, jammer, simulation_continues)

        clock.tick(60)

if __name__ == "__main__":
    main()


