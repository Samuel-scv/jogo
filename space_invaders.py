import pygame
import sys
import json
import os
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BG_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
GREEN = (50, 255, 50)
RED = (255, 50, 50)
YELLOW = (255, 255, 50)
BLUE = (50, 150, 255)
PURPLE = (150, 50, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Courier", 24, bold=True)
font_medium = pygame.font.SysFont("Courier", 36, bold=True)
font_large = pygame.font.SysFont("Courier", 64, bold=True)

ARQUIVO_RANKING = "ranking.json"

# ------------------------ SISTEMA DE RANKING ------------------------
def carregar_ranking():
    if os.path.exists(ARQUIVO_RANKING):
        try:
            with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_ranking(nome, pontos, tempo):
    ranking = carregar_ranking()
    ranking.append({"nome": nome, "pontos": pontos, "tempo": tempo})
    ranking.sort(key=lambda x: (-x['pontos'], x['tempo']))
    ranking = ranking[:10] 
    
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
        json.dump(ranking, f, ensure_ascii=False, indent=4)


# ------------------------ CLASSES DO JOGO ------------------------
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.hp = 3
        self.image = pygame.Surface((70, 40))
        self.image.fill(BLUE) 
        self.rect = self.image.get_rect(topleft=(x, y))

    def take_damage(self):
        self.hp -= 1
        if self.hp == 2:
            self.image.fill(PURPLE) 
        elif self.hp == 1:
            self.image.fill(RED)    
        elif self.hp <= 0:
            self.kill()             

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, speed, color):
        super().__init__()
        self.image = pygame.Surface((4, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("graphics/player.png").convert_alpha()
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
        self.speed = 6
        self.lasers = pygame.sprite.Group()
        
        self.ready_to_shoot = True
        self.laser_time = 0
        self.laser_cooldown = 400 

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.ready_to_shoot:
            self.shoot_laser()
            self.ready_to_shoot = False
            self.laser_time = pygame.time.get_ticks()

    def recharge(self):
        if not self.ready_to_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready_to_shoot = True

    def constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.midtop, -8, WHITE))

    def update(self):
        self.get_input()
        self.constraint()
        self.recharge()
        self.lasers.update()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, cor):
        super().__init__()
        caminho_imagem = f"graphics/{cor}.png"
        self.image = pygame.image.load(caminho_imagem).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, direction):
        self.rect.x += direction

# ------------------------ TELAS ------------------------
def tela_menu():
    while True:
        screen.fill(BG_COLOR)
        
        titulo = font_large.render("SPACE INVADERS", True, GREEN)
        opt1 = font_medium.render("1. JOGAR", True, WHITE)
        opt2 = font_medium.render("2. RANKING", True, WHITE)
        opt3 = font_medium.render("3. SAIR", True, RED)
        
        screen.blit(titulo, (SCREEN_WIDTH//2 - titulo.get_width()//2, 100))
        screen.blit(opt1, (SCREEN_WIDTH//2 - opt1.get_width()//2, 250))
        screen.blit(opt2, (SCREEN_WIDTH//2 - opt2.get_width()//2, 320))
        screen.blit(opt3, (SCREEN_WIDTH//2 - opt3.get_width()//2, 390))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "SAIR"
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_KP1]: return "JOGAR"
                if event.key in [pygame.K_2, pygame.K_KP2]: return "RANKING"
                if event.key in [pygame.K_3, pygame.K_KP3]: return "SAIR"
                    
        pygame.display.flip()
        clock.tick(FPS)

def tela_ranking():
    ranking = carregar_ranking()
    while True:
        screen.fill(BG_COLOR)
        
        titulo = font_large.render("TOP 10 RANKING", True, YELLOW)
        screen.blit(titulo, (SCREEN_WIDTH//2 - titulo.get_width()//2, 30))
        
        y_pos = 120
        if not ranking:
            texto = font_small.render("Nenhum recorde ainda!", True, WHITE)
            screen.blit(texto, (SCREEN_WIDTH//2 - texto.get_width()//2, y_pos))
        else:
            for i, jogador in enumerate(ranking):
                nome = jogador.get('nome', 'Anônimo')
                texto = font_small.render(f"{i+1}º {nome[:10]:<10} | {jogador['pontos']:>4} pts | {jogador['tempo']:>3}s", True, WHITE)
                screen.blit(texto, (SCREEN_WIDTH//2 - texto.get_width()//2, y_pos))
                y_pos += 35
            
        rodape = font_small.render("Pressione ESC para voltar", True, BLUE)
        screen.blit(rodape, (SCREEN_WIDTH//2 - rodape.get_width()//2, SCREEN_HEIGHT - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 

        pygame.display.flip()
        clock.tick(FPS)

def tela_inserir_nome(pontos, tempo):
    nome = ""
    while True:
        screen.fill(BG_COLOR)
        
        msg1 = font_medium.render("FIM DE PARTIDA!", True, YELLOW)
        msg2 = font_small.render(f"Pontos: {pontos}  |  Tempo: {tempo}s", True, WHITE)
        msg3 = font_medium.render("Digite seu nome:", True, GREEN)
        nome_texto = font_large.render(nome, True, BLUE)
        
        screen.blit(msg1, (SCREEN_WIDTH//2 - msg1.get_width()//2, 100))
        screen.blit(msg2, (SCREEN_WIDTH//2 - msg2.get_width()//2, 160))
        screen.blit(msg3, (SCREEN_WIDTH//2 - msg3.get_width()//2, 280))
        screen.blit(nome_texto, (SCREEN_WIDTH//2 - nome_texto.get_width()//2, 350))
        
        rodape = font_small.render("Pressione ENTER para salvar", True, RED)
        screen.blit(rodape, (SCREEN_WIDTH//2 - rodape.get_width()//2, 500))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return nome.strip() if nome.strip() != "" else "Desconhecido"
                elif event.key == pygame.K_BACKSPACE:
                    nome = nome[:-1] 
                else:
                    if event.unicode.isprintable() and len(nome) < 12:
                        nome += event.unicode

        pygame.display.flip()
        clock.tick(FPS)


# ------------------------ Partida ------------------------
def jogar_partida():
    player = pygame.sprite.GroupSingle(Player())
    
    aliens = pygame.sprite.Group()
    alien_lasers = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    
    linhas, colunas = 5, 10
    x_offset, y_offset = 60, 48
    for row in range(linhas):
        for col in range(colunas):
            x = 100 + col * x_offset
            y = 50 + row * y_offset
            
            
            if row == 0:
                cor_alien = 'yellow'
            elif 1 <= row <= 2:
                cor_alien = 'green'
            else:
                cor_alien = 'red'
                
            aliens.add(Alien(x, y, cor_alien))

   
    espacamento = SCREEN_WIDTH / 5
    for i in range(4):
        x = espacamento * (i + 1) - 35
        y = SCREEN_HEIGHT - 130
        obstacles.add(Obstacle(x, y))

    alien_direction = 2
    score = 0
    vidas = 3
    start_ticks = pygame.time.get_ticks()

    def alien_setup():
        nonlocal alien_direction
        all_aliens = aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= SCREEN_WIDTH or alien.rect.left <= 0:
                alien_direction *= -1
                for a in all_aliens:
                    a.rect.y += 20 
                break

    def alien_shoot():
        if aliens.sprites():
            random_alien = random.choice(aliens.sprites())
            laser_sprite = Laser(random_alien.rect.midbottom, 6, YELLOW)
            alien_lasers.add(laser_sprite)

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800) 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                alien_shoot()

        screen.fill(BG_COLOR)
        tempo_atual = (pygame.time.get_ticks() - start_ticks) // 1000

        player.update()
        alien_lasers.update()
        aliens.update(alien_direction)
        alien_setup()

        
        if player.sprite.lasers:
            for laser in player.sprite.lasers:
                aliens_hit = pygame.sprite.spritecollide(laser, aliens, True)
                if aliens_hit:
                    laser.kill()
                    score += 10 * len(aliens_hit)

        
        if player.sprite.lasers:
            for laser in player.sprite.lasers:
                obs_hit = pygame.sprite.spritecollide(laser, obstacles, False)
                if obs_hit:
                    laser.kill()


        if alien_lasers:
            for laser in alien_lasers:
                if pygame.sprite.spritecollide(laser, player, False):
                    laser.kill()


        if alien_lasers:
            for laser in alien_lasers:
                obs_hit = pygame.sprite.spritecollide(laser, obstacles, False)
                if obs_hit:
                    laser.kill()
                    for obs in obs_hit:
                        obs.take_damage()

        game_over = False
        if vidas <= 0 or len(aliens) == 0:
            game_over = True
            
        for alien in aliens.sprites():
            if alien.rect.bottom >= player.sprite.rect.top:
                game_over = True
                break

        if game_over:
            pygame.time.set_timer(ALIENLASER, 0) 
            return score, tempo_atual

        player.draw(screen)
        player.sprite.lasers.draw(screen)
        aliens.draw(screen)
        alien_lasers.draw(screen)
        obstacles.draw(screen)


        score_surf = font_small.render(f"SCORE: {score}", False, WHITE)
        screen.blit(score_surf, (10, 10))
        
        vidas_surf = font_small.render(f"VIDAS: {vidas}", False, RED)
        screen.blit(vidas_surf, (SCREEN_WIDTH//2 - vidas_surf.get_width()//2, 10))

        tempo_surf = font_small.render(f"TEMPO: {tempo_atual}s", False, WHITE)
        screen.blit(tempo_surf, (SCREEN_WIDTH - tempo_surf.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(FPS)

def main():
    while True:
        escolha = tela_menu()
        
        if escolha == "JOGAR":
            pontos, tempo = jogar_partida()
            nome = tela_inserir_nome(pontos, tempo)
            salvar_ranking(nome, pontos, tempo)
            
        elif escolha == "RANKING":
            tela_ranking()
            
        elif escolha == "SAIR":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()