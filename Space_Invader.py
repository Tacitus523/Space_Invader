import pygame
from pygame import mixer
import os
from math import sqrt
from PIL import Image

#Change directory
os.chdir(os.path.dirname(__file__))

#Highscore
with open('highscore.txt','r') as f:
    highscore=f.readline()

#Initilaze
pygame.font.init()
pygame.mixer.init()

#Screen settings
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Space Invader")
icon = pygame.image.load('ship.png')
pygame.display.set_icon(icon)
#Icons made by <a href="https://www.flaticon.com/authors/photo3idea-studio" title="photo3idea_studio">photo3idea_studio</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>
#Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>


#Music and Sounds
game_over_sound=mixer.Sound('explosion.wav')
laser_sound=mixer.Sound('laser.wav')
hit_sound=mixer.Sound('destroy.wav')
mixer.music.load('background.wav')
pygame.mixer.music.set_volume(0.3)
mixer.music.play(-1,fade_ms=5000)

class Object():
    image='laser.png'
    img=pygame.image.load(image)
    img_size=Image.open(image).size[0]
    def __init__(self,x,y):
        self.x=x
        self.y=y
        
    
    def show(self):
        screen.blit(self.img,(self.x,self.y))

class Player(Object):
    image='ship.png'
    img=pygame.image.load(image)
    img_size=Image.open(image).size[0]
    score=0
    def __init__(self,x,y):
        super().__init__(x,y)
        self.x_change=0.25
        self.movment=0

    def move(self):
        self.x += self.movment
        if self.x < 5:
            self.x = 5
        elif self.x > 800-self.img_size-5:
            self.x = 800-self.img_size-5
        self.show()

class Enemy(Object):
    image='alien1.png'
    img=pygame.image.load(image)
    img_size=Image.open(image).size[0]
    enemies=[]
    max_y=0
    x_move=0.1
    def __init__(self,x,y):
        super().__init__(x,y)
        self.enemies.append(self)

    def __del__(self):
        if self in Enemy.enemies:
            Enemy.enemies.remove(self)

    @classmethod
    def get_max_y(cls):
        max_y=0
        for enemy in cls.enemies:
            if enemy.y>max_y:
                max_y=enemy.y
        return max_y

    @classmethod
    def move(cls):
        y_change=cls.img_size*1.2
        for enemy in cls.enemies:
            if enemy.x <=5:
                cls.x_move*=-1
                for i in cls.enemies:
                    i.y += y_change
                cls.max_y=cls.get_max_y()
                break
            elif enemy.x >= 800-cls.img_size-5:
                cls.x_move*=-1
                for i in cls.enemies:
                    i.y += y_change
                cls.max_y=enemy.y
                break

        for enemy in cls.enemies:
            enemy.x -= cls.x_move
            enemy.show()

    @classmethod
    def spawn(cls,num):
        left=120
        top=50
        for _ in range(num):
            Enemy(left,top)
            left+=40
            if left>480:
                left=120
                top+=30

    @classmethod
    def next_wave(cls):
        if not len(cls.enemies):
            if cls.x_move<0:
                cls.x_move-=0.1
            else:
                cls.x_move+=0.1
            cls.spawn(20)
            cls.max_y=cls.get_max_y()
            
class Laser(Object):
    image='laser.png'
    img=pygame.image.load(image)
    img_size=Image.open(image).size[0]
    ammo=3
    active=[]

    def __init__(self,x,y):
        super().__init__(x,y)
        self.x=x+6
        self.y=y-35
        laser_sound.play()
        Laser.ammo-=1

    def __del__(self):
        Laser.ammo+=1
        if self in Laser.active:
            Laser.active.remove(self)

    @classmethod
    def move(cls):
        y_move=0.5
        for laser in cls.active:    
            laser.y -= y_move
            laser.show()
            if laser.y<=10:
                del cls.active[cls.active.index(laser)]

    @classmethod     
    def fire_laser(cls,x,y):
        if cls.ammo:
            cls.active.append(Laser(x,y))
        
class Font():
    font=pygame.font.SysFont('forte',24)
    game_over_y=0
    @classmethod
    def show_score(cls):
        x=10
        y=10
        score=cls.font.render("Score: "+str(Player.score),True,(0,0,0))
        screen.blit(score,(x,y))
    
    @classmethod
    def show_ammo(cls):
        x=650
        y=10
        img=pygame.image.load('laser.png')
        ammo=cls.font.render("Ammo:",True,(0,0,0))
        screen.blit(ammo,(x,y))
        if Laser.ammo>=1:
            screen.blit(img,(x+80,y))
        if Laser.ammo>=2:
            screen.blit(img,(x+100,y))
        if Laser.ammo>=3:
            screen.blit(img,(x+120,y))

    @classmethod
    def show_game_over(cls):
        font=pygame.font.SysFont('impact',70)
        game_over_font=font.render("GAME OVER",True,(0,0,0))
        font=pygame.font.SysFont('impact',30)
        score_font=font.render("Score: "+str(Player.score),True,(0,0,0))
        highscore_font=font.render("Highscore: "+str(highscore),True,(0,0,0))
        x=250
        y=0
        while y<=250:
            y+=1
            screen.fill((255,255,255))
            screen.blit(game_over_font,(x,y))
            pygame.time.wait(5)
            pygame.display.update()
        screen.blit(score_font,(x,y+80))
        screen.blit(highscore_font,(x,y+120))
        pygame.display.update()
        pygame.time.wait(3000)

def play_space_invader():
    def game_over():
        if Enemy.max_y>500:
            pygame.mixer.music.fadeout(5000)
            game_over_sound.play()
            for _ in range(len(Enemy.enemies)):
                del Enemy.enemies[0]
            for _ in range(len(Laser.active)):
                del Laser.active[0]
            player.y=1000
            return True

    def collision():
        for laser in Laser.active:
            for enemy in Enemy.enemies:
                distance=sqrt((enemy.x-laser.x)**2+(enemy.y-laser.y)**2)
                if distance<25:
                    Player.score+=1
                    hit_sound.play()
                    if enemy in Enemy.enemies:
                        del Enemy.enemies[Enemy.enemies.index(enemy)]
                    if laser in Laser.active:
                        del Laser.active[Laser.active.index(laser)]
                    
    Player.score=0
    player=Player(370,565)
    Enemy.x_move=0.1
    Enemy.next_wave()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.movment=-player.x_change
                if event.key == pygame.K_RIGHT:
                    player.movment=player.x_change
                if event.key == pygame.K_SPACE:
                    Laser.fire_laser(player.x,player.y)
            if event.type == pygame.KEYUP:     
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.movment=0

        #RGB
        screen.fill((255,255,255))
        player.move()
        Enemy.move()
        Laser.move()
        collision()
        Enemy.next_wave()
        Font.show_score()
        Font.show_ammo()
        pygame.display.update()

        if game_over():
            pygame.display.update()
            Font.show_game_over()
            break
    
    if Player.score>int(highscore):
        with open('highscore.txt','w') as f:
            try:
                f.write(str(Player.score))
            except:
                pass

if __name__ == "__main__":
    play_space_invader()
