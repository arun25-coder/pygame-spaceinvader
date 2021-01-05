import pygame
import os
import random

#GAME SETTINGS
pygame.font.init()
pygame.init()
X = 600  #Width
Y = 600  #Height
WIN = pygame.display.set_mode((X, Y))
pygame.display.set_caption('Space Invader')
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","bg.jpg")),(X,Y))

#Hero ship
hero = pygame.transform.scale(pygame.image.load(os.path.join("assets","pixel_ship_yellow.png")),(50,50))
yellow_laser = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

#Enemy Ship
red_ship = pygame.transform.scale(pygame.image.load(os.path.join("assets","pixel_ship_red_small.png")),(300,150))
red_laser = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
green_ship = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
green_laser = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
blue_ship = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))
blue_laser = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))

#Abstract
class Ship:
    COOLDOWN = 30 #30 seconds interval to release laser from enemies

    def __init__(self,x,y,health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self,window):
        #pygame.draw.rect(window, (255,0,0), (self.x,self.y,40,40))
        window.blit(self.ship_img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self,speed,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(Y): #Height
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                if laser in self.lasers:
                    self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-25,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self,x,y,health=100,point=0):
        super().__init__(x,y,health)
        self.ship_img = hero
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)#to tell us if we hit pixel
        self.max_health = health
        self.point = point

    def move_lasers(self,speed,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(Y): #Heightd
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.point += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self,window):
        pygame.draw.rect(window,(255,0,0),(self.x,self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 5))
        pygame.draw.rect(window, (0, 255, 0),(self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 5))

class Enemy(Ship):
    COLOR_MAP = {
        "red": (red_ship,red_laser) ,
        "blue": (blue_ship,blue_laser),
        "green": (green_ship,green_laser)
    }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img , self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)  # to tell us if we hit pixel
        self.max_health = health

    def move(self,speed):
        self.y += speed

class Laser():
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)  # to tell us if we hit pixel

    def draw(self,window):
        window.blit(self.img, (self.x,self.y))

    def move(self,speed):
        self.y += speed

    def off_screen(self,height):
        return not(self.y <= height and self.y >= 0)

    def collision(self,obj):
        return collide(self,obj)

def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None  #(x,y)


def main():
    run = True
    FPS = 50
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans",30)
    lost_font = pygame.font.SysFont("comicsans",50)
    clock = pygame.time.Clock()
    player_speed = 5
    player = Player(X//2-25,Y-100)
    laser_speed = 5
    enemies = []
    wavelength = 0
    enemy_speed = 1
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG,(0,0))
        lives_label = main_font.render(f"lives: {lives}", 1, (255, 255, 0))
        level_label = main_font.render(f"level: {level}", 1, (255, 255, 255))
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(X - level_label.get_width() - 10, 10))
        player.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!",1,(255,255,255))
            WIN.blit(lost_label, (X/2 - lost_label.get_width()/2,250))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if(lives <= 0 or player.health <= 0):
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if(len(enemies) == 0):
            level += 1
            wavelength += 5
            if(level == 'NA'):
                enemies.append(Enemy(X//2-100, -500, 'red', 150))
                enemy_speed = 1
            else:
                for i in range(wavelength):
                    enemy = Enemy(random.randrange(50,X-100), random.randrange(-1500,-100), random.choice(['green','blue']))
                    enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_speed > 0:#left
            player.x -= player_speed
        if keys[pygame.K_d] and player.x + player_speed + player.get_width() < X:#right
            player.x += player_speed
        if keys[pygame.K_w] and player.y - player_speed > 0:#up
            player.y -= player_speed
        if keys[pygame.K_s] and player.y + player_speed + player.get_height() + 12 < Y:#down
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies:
            enemy.move(enemy_speed)
            enemy.move_lasers(laser_speed,player)

            #Random laser shoot from enemies
            if random.randrange(0, 4*60) == 1:
                enemy.shoot()

            #Collide between enemy and player
            if collide(enemy,player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > X:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_speed, enemies)  #negative to bullet go upside for player

    return player.point

def main_menu():
    run = True
    title_font = pygame.font.SysFont("comicsons",30)
    title_label = title_font.render("Press Mouse to begin...", 1, (255, 255, 255))
    title_start = title_font.render("Start(Y)",1,(255,255,255))
    title_quit = title_font.render("Quit(X)", 1, (255, 255, 255))
    while run:
        WIN.blit(BG, (0, 0))
        WIN.blit(title_label, (X / 2 - title_label.get_width() / 2, 300))
        WIN.blit(title_start, (10, Y-60))
        WIN.blit(title_quit, (10, Y - 30))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_x] or keys[pygame.K_n]:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN or keys[pygame.K_y]:
                point = main()
                title_label = title_font.render("Your Best Score: "+str(point)+"",1,(0,255,0))
                title_start = title_font.render("Restart(Y/N)", 1, (255, 255, 255))

    pygame.quit()


if __name__ == '__main__':
    main_menu()
