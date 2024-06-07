import pygame
from pygame.locals import *
import random
import pickle

#Inisialisasi game
pygame.init()

# Set clock dan frame per detik (fps)
clock = pygame.time.Clock()
fps = 60

# Definisikan ukuran layar
screen_width = 576
screen_height = 624

# Set mode layar
screen = pygame.display.set_mode((screen_width, screen_height)) #mengatur layar dengan lebar dan tinggi tertentu
pygame.display.set_caption('Flappy Ladybug')

# Definisikan font
font_score = pygame.font.SysFont('Bauhaus 93', 60)
font_high_score = pygame.font.SysFont('Bauhaus 93', 20)
font_description = pygame.font.SysFont('Calibri', 20, bold=True)

# Definisikan warna font
white = (255, 255, 255)
black = (0, 0, 0)

# Variabel permainan
ground_scroll = 0
scroll_speed = 3
flying = False
game_over = False
start_clicked = False
fence_gap = 100 #jarak antara rintangan atas dan bawah
fence_frequency = 1000 #frekuaensi pembuatan rintangan (milliseconds)
last_fence = pygame.time.get_ticks() - fence_frequency # Menandai waktu terakhir munculnya rintangan
score = 0 
pass_fence = False #status yang menandakan apakah ladybug sudah melewati rintangan atau belum



#Gambar yang digunakan
bg = pygame.image.load('picture/Background.png')
ground_img = pygame.image.load('picture/ground.png')
start_img = pygame.image.load('picture/start.png')
restart_img = pygame.image.load('picture/restart.png')
reset_img = pygame.image.load('picture/reset.png')


# Kelas Ladybug
class Ladybug(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []    # Menyimpan daftar gambar animasi ladybug
        self.index = 0      # Indeks gambar saat ini dalam daftar gambar animasi
        self.counter = 0    # Menghitung jumlah siklus untuk mengatur kecepatan animasi
        for num in range(1, 5): # loop untuk memuat gambar animasi ladybug
            img = pygame.image.load(f'picture/ladybug{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]    # Menetapkan gambar saat ini sebagai gambar animasi ladybug
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]   # Menetapkan posisi awal ladybug
        self.vel = 0        # Kecepatan vertikal ladybug
        self.clicked = False    # Menandai apakah tombol mouse ditekan

    def update(self):

        if flying == True:
			#gravtasi
            self.vel += 0.25    # Menetapkan gambar saat ini sebagai gambar animasi ladybug
            if self.vel > 8:    # Batasi kecepatan maksimum ladybug saat jatuh
                self.vel = 8
            if self.rect.bottom < (screen_height - ground_img.get_height()):
                self.rect.y += int(self.vel)
    
        if game_over == False:
			#jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -5
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False


            # handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #rotate the ladybug
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


# Kelas Fence
class Fence(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('picture/Fence.png')
        self.rect = self.image.get_rect()
		#position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(fence_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(fence_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
        	self.kill()

# Kelas Button
class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):

		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check if mouse is over the button
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action
     
# Grup sprite ladybug dan fence
ladybug_group = pygame.sprite.Group()
fence_group = pygame.sprite.Group()

# Objek ladybug
flappy = Ladybug(100, int(screen_height / 2))
ladybug_group.add(flappy)


# Fungsi untuk menampilkan teks
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col) # Membuat gambar teks dengan font, teks, dan warna yang diberikan
    screen.blit(img, (x, y))  # Menempatkan gambar teks ke posisi (x, y) pada layar


# Fungsi untuk mereset permainan
def reset_game():
	fence_group.empty()
	flappy.rect.x = 100 # Mengatur posisi ladybug
	flappy.rect.y = int(screen_height / 2)
	score = 0
	return score

# Fungsi untuk memuat skor tertinggi
def load_high_score():
    try:
        with open("highscore.dat", "rb") as file:
            high_score = pickle.load(file)
    except (OSError, IOError, EOFError):
        high_score = 0
    return high_score


# Fungsi untuk menyimpan skor tertinggi
def save_high_score(score, high_score):
    if score > high_score:
        high_score = score
        with open("highscore.dat", "wb") as file:
            pickle.dump(high_score, file)
    return high_score

# Muat skor tertinggi
high_score = load_high_score()


# Fungsi untuk mereset skor tertinggi
def reset_high_score():
    high_score = 0
    with open("highscore.dat", "wb") as file:
        pickle.dump(high_score, file)
    return high_score


# Objek tombol
start = Button(screen_width // 2 - start_img.get_width() // 2, 500, start_img)
restart = Button(screen_width // 2 - 50, screen_height // 2 - 100, restart_img)
reset = Button(screen_width // 20, 50, reset_img)


# Loop permainan
run = True
while run:
    clock.tick(fps)

    # Bagian sebelum permainan dimulai
    if not start_clicked:
        screen.blit(bg, (0, 0))

        # Menambahkan deskripsi permainan
        description_text = [
            "Cara Bermain :",
            "1. Mulai permainan dengan menekan tombol Start di layar", 
            "    utama.",
            "2. Gunakan tombol kiri mouse untuk mengendalikan gerakan ",
            "    ladybug. Klik untuk membuat ladybug naik, lepas klik untuk", 
            "    membuat ladybug turun.",
            "3. Hindari menabrak rintangan pagar kayu. Jika ladybug", 
            "    menabrak, permainan akan berakhir.",
            "4. Jika ingin mengulang permainan, tekan tombol Restart di",
            "    layar permainan.",
            "5. Klik tombol Reset untuk menjadikan score terakhir menjadi",
            "    score tertinggi",
            "6. Setelah selesai bermain, klik tombol Close pada Windows ", 
            "    untuk menutup permainan.",
            " ",
            "                                  SELAMAT BERMAIN :)"
        ]
        transparent_white = (255, 255, 255, 150)
        description_box = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        description_box.fill(transparent_white)
        screen.blit(description_box, (0, 0))
        for i, line in enumerate(description_text):
            text_render = font_description.render(line, True, black)
            screen.blit(text_render, (30, 60 + i * 25))

        # Menambahkan tombol start
        start_action = start.draw()
        if start_action:
            start_clicked = True
            description_text.clear()
            ladybug_group.add(flappy)


    # Bagian saat permainan berlangsung
    else:

        screen.blit(bg, (0, 0))  # Gambar latar belakang
        ladybug_group.draw(screen)  # Gambar sprite dari ladybug_group
        ladybug_group.update()  # Memanggil metode update
        fence_group.draw(screen) # Gambar sprite dari fence_group
            
        screen.blit(ground_img, (ground_scroll, screen_height - ground_img.get_height()))  # Gambar ground
        
        #Untuk mengecek score
        if len(fence_group) > 0:
            if ladybug_group.sprites()[0].rect.left > fence_group.sprites()[0].rect.left\
                and ladybug_group.sprites()[0].rect.right < fence_group.sprites()[0].rect.right\
                and pass_fence == False:
                pass_fence = True
            if pass_fence == True:
                if ladybug_group.sprites()[0].rect.left > fence_group.sprites()[0].rect.right:
                    score += 1
                    pass_fence = False


        draw_text(str(score), font_score, white, int(screen_width / 2), 20)
        draw_text("High Score: " + str(high_score), font_high_score, black , 20, 20)


        #mendeteksi tabrakan
        if pygame.sprite.groupcollide(ladybug_group, fence_group, False, False) or flappy.rect.top < 0:
            game_over = True

        #mendeteksi ladybug jatuh  
        if flappy.rect.bottom > (screen_height - ground_img.get_height()):
            game_over = True
            flying = False
        
        
        if game_over == False:
            
            #membuat penghalang (pagar) baru
            time_now = pygame.time.get_ticks()
            if time_now - last_fence > fence_frequency:
                fence_height = random.randint(-100, 100)
                btm_fence = Fence(screen_width, int(screen_height / 2) + fence_height, -1)
                top_fence = Fence(screen_width, int(screen_height / 2) + fence_height, 1)
                fence_group.add(btm_fence)
                fence_group.add(top_fence)
                last_fence = time_now


            #draw and scroll the ground
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

            fence_group.update()

        if reset.draw() == True:
            high_score = reset_high_score()
        
        #Bagian saat permainan berakhir
        if game_over == True:
            high_score = save_high_score(score, high_score)
            if restart.draw() == True:
                game_over = False
                score = reset_game()
            if reset.draw():  # Memeriksa jika tombol reset skor tertinggi ditekan
                high_score = reset_high_score()
        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
        
            
    pygame.display.update()  # Update layar

pygame.quit()
