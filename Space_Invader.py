import pygame
from pygame import mixer
import os

#Change directory
os.chdir(os.path.dirname(__file__))

#Highscore
with open('highscore.txt','r') as f:
    highscore=f.readline()

#Initilaze
pygame.font.init()
pygame.mixer.init()

#Screen settings
WIDTH,HEIGHT=800,600
screen = pygame.display.set_mode((WIDTH,HEIGHT))
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

#Baseclass
class Object():
    img=None
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.mask=pygame.mask.from_surface(self.img)
        
    def show(self):
        screen.blit(self.img,(self.x,self.y))

    def get_width(self):
        return pygame.image.get_width(self.img)

    def get_height(self):
        return pygame.image.get_height(self.img)

    def collide(self, other):
        delta_x = int(self.x-other.x)
        delta_y = int(self.y-other.y)
        return self.mask.overlap(other.mask,(delta_x,delta_y)) != None

#Playerclass

class Player(Object):
    score=0
    img=pygame.image.load('ship.png')
    def __init__(self,x,y):
        super().__init__(x,y)
        self.x_change=4
        self.movment=0

class Enemy(Object):
    enemies=[]
    max_y=0
    x_move=0
    img=pygame.image.load('alien1.png')
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
        y_change=cls.img.get_height()*1.2
        for enemy in cls.enemies:
            if enemy.x <=5:
                cls.x_move*=-1
                for i in cls.enemies:
                    i.y += y_change
                cls.max_y=cls.get_max_y()
                break
            elif enemy.x >= 800-cls.img.get_height()-5:
                cls.x_move*=-1
                for i in cls.enemies:
                    i.y += y_change
                cls.max_y=enemy.y
                break
        for enemy in cls.enemies:
            enemy.x -= cls.x_move

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
                cls.x_move-=1
            else:
                cls.x_move+=1
            cls.spawn(20)
            cls.max_y=cls.get_max_y()
            
class Laser(Object):
    ammo=3
    active=[]
    img=pygame.image.load('laser.png')
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
        y_move=7
        for laser in cls.active:    
            laser.y -= y_move
            if laser.y<=10:
                del cls.active[cls.active.index(laser)]

    @classmethod     
    def fire_laser(cls,x,y):
        if cls.ammo:
            cls.active.append(Laser(x,y))

def play_space_invader():
    #reset variables
    Player.score=0
    player=Player(370,565)
    Enemy.x_move=1
    Enemy.next_wave()
    mainfont=pygame.font.SysFont('forte',24)

    #set Clock
    FPS = 60
    clock = pygame.time.Clock()

    def game_over():
        def show_game_over():
            game_over_font=pygame.font.SysFont('impact',70)
            score_font=pygame.font.SysFont('impact',30)

            game_over_label=game_over_font.render("GAME OVER",True,(0,0,0))
            score_label=score_font.render("Score: "+str(Player.score),True,(0,0,0))
            highscore_label=score_font.render("Highscore: "+str(highscore),True,(0,0,0))

            x=250
            y=0
            while y<=250:
                y+=1
                screen.fill((255,255,255))
                screen.blit(game_over_label,(x,y))
                pygame.time.wait(4)
                pygame.display.update()

            screen.blit(score_label,(x,y+80))
            screen.blit(highscore_label,(x,y+120))
            pygame.display.update()
            pygame.time.wait(3000)
   
        if Enemy.max_y>500:
            pygame.mixer.music.fadeout(5000)
            game_over_sound.play()
            for _ in range(len(Enemy.enemies)):
                del Enemy.enemies[0]
            for _ in range(len(Laser.active)):
                del Laser.active[0]
            player.y=1000
            show_game_over()

            #update highscore
            if Player.score>int(highscore):
                with open('highscore.txt','w') as f:
                    try:
                        f.write(str(Player.score))
                    except:
                        pass

            return True

    def collision():
        for laser in Laser.active:
            for enemy in Enemy.enemies:
                if enemy.collide(laser):
                    Player.score+=1
                    hit_sound.play()
                    if enemy in Enemy.enemies:
                        Enemy.enemies.remove(enemy)
                    if laser in Laser.active:
                        Laser.active.remove(laser)

    def redraw_objects():
        def show_ammo():
            x=650
            y=10
            ammo=mainfont.render("Ammo:",True,(0,0,0))
            screen.blit(ammo,(x,y))
            if Laser.ammo>=1:
                screen.blit(Laser.img,(x+80,y))
            if Laser.ammo>=2:
                screen.blit(Laser.img,(x+100,y))
            if Laser.ammo>=3:
                screen.blit(Laser.img,(x+120,y))
        
        #RGB
        screen.fill((255,255,255))
        score=mainfont.render("Score: "+str(Player.score),True,(0,0,0))
        screen.blit(score,(10,10))
        show_ammo()
        player.show()
        for enemy in Enemy.enemies:
            enemy.show()
        for laser in Laser.active:
            laser.show()
        pygame.display.update()

    running = True
    while running:
        clock.tick(FPS)

        #Keyyboard Interaction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_SPACE:   
                Laser.fire_laser(player.x,player.y)
                
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player.x_change >= 5:
            player.x -= player.x_change
        if keys[pygame.K_RIGHT] and player.x + player.x_change <= WIDTH-player.img.get_width()-5:
            player.x += player.x_change
        
        Enemy.move()
        Laser.move()
        collision()
        Enemy.next_wave()

        redraw_objects()

        if game_over():
            break
    
def main_menu():
    menu_font=pygame.font.SysFont('impact',40)
    title_label=menu_font.render("Space Invader",True,(0,0,0))
    menu_label=menu_font.render("Press Enter to play",True,(0,0,0))
    running=True
    while running:
        screen.fill((255,255,255))
        screen.blit(title_label,((WIDTH-title_label.get_width())/2,(HEIGHT-menu_label.get_height()-100)/2))
        screen.blit(menu_label,((WIDTH-menu_label.get_width())/2,(HEIGHT-menu_label.get_height())/2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                play_space_invader()
    pygame.quit()


if __name__ == "__main__":
    main_menu()
