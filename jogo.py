# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import resource
import math, time
import random

###
#classe que monta os limites da área de jogo
###
class Area(object):

    def __init__(self,screen,bola):
        self.screen = screen
        self.parede_left = resource.img_parede_left
        self.parede_right = resource.img_parede_right
        self.parede_top = resource.img_parede_top
        self.rect_bottom = pygame.Rect((0,765),(1024,3))
        self.batida = False
        self.bola = bola

    def bateu(self):
        left = self.parede_left.get_rect()
        left.topleft = (0,0)
        right = self.parede_right.get_rect()
        right.topleft = (896,0)
        top = self.parede_top.get_rect()
        top.topleft = (0,0)
        objeto_valido=True
        if(not self.batida):
            if(left.colliderect(self.bola.getRect()) or right.colliderect(self.bola.getRect())):
                self.bola.vertical()         
                self.batida=True
            elif(top.colliderect(self.bola.getRect())):
                self.bola.horizontal()
                self.batida=True
            elif(self.rect_bottom.colliderect(self.bola.getRect())):
                objeto_valido=False
        else:
            if(not (left.colliderect(self.bola.getRect()) or right.colliderect(self.bola.getRect()) or top.colliderect(self.bola.getRect()) or self.rect_bottom.colliderect(self.bola.getRect()))):
                self.batida=False
        return objeto_valido
    
    def draw(self):
        self.screen.blit(self.parede_left,(0,0))
        self.screen.blit(self.parede_right,(896,0))
        self.screen.blit(self.parede_top,(0,0))

	
###
#classe que le o conteudo de um arquivo e retorna em uma string
###
class Arquivo(object):

    #le o arquifo "fases/"+(nome_da_fase)
    def abrir(self,fase):
        fonte = "fases/" + fase
        linha = ""
        try:
            arquivo = open(fonte,"r")
            linha = arquivo.read()
            arquivo.close();
        except:
            print "Nao foi possivel abrir o arquivo."

        return linha


###
#Classe que define um bloco
###
class Bloco(object):
    def __init__(self,screen,pos,fase):
        self.ativo = True
        self.pos = pos
        self.img = ""
        self.screen = screen
        self.batida=False
	self.width=44
	self.height=15
	self.fase=fase

    #Verifica se a bola bateu no bloco
    def bateu(self,bola):
        im_rect = self.img.get_rect().move(self.pos[0],self.pos[1])
        x =  im_rect.colliderect(bola.getRect())
        if(x and not self.batida):
	    print "entrou"
            self.batida=True
            rect_left = pygame.Rect(self.pos,(5,self.height))
            rect_right = pygame.Rect((self.pos[0]+self.width-5,self.pos[1]),(5,self.height))
            rect_top = pygame.Rect((self.pos[0],self.pos[1]),(self.width,5))
            rect_bottom = pygame.Rect((self.pos[0],self.pos[1]+self.height-5),(self.width,5))

            if(rect_left.colliderect(bola.getRect()) or rect_right.colliderect(bola.getRect())):
                bola.vertical()
		print "bateu vertical"
	    if(rect_top.colliderect(bola.getRect()) or rect_bottom.colliderect(bola.getRect())):
                bola.horizontal()
		print "bateu horizontal"            

            self.trata_batida(bola)
        else:
	    if(not x):
		self.batida=False
        return x

    #Desenha o bloco na tela
    def draw(self):
        self.screen.blit(self.img,self.pos)

    #destroi o bloco
    def destroi(self):
        self.ativo = False
	self.fase.remover_bloco(self)

###
#Classe que especializa o bloco comum
###
class Bloco0(Bloco): 
    def __init__(self,screen,pos,score,fase):
        Bloco.__init__(self,screen,pos,fase)
        self.img = resource.img_bl1
	self.score = score

    #rotina de tratamento da batida da bola
    def trata_batida(self,bola):
	self.score.add(10)
        self.destroi()   

###
#Classe que especializa o bloco de velocidade
###
class Bloco1(Bloco): 
    def __init__(self,screen,pos,score,fase):
        Bloco.__init__(self,screen,pos,fase)
        self.img = resource.img_bl2
	self.score = score
	
    #rotina de tratamento da batida da bola
    def trata_batida(self,bola):
	self.score.add(20)
        self.destroi()   
        bola.incSpeed()

###
#Classe que especializa o bloco que precisa de 2 batidas para sumir
###
class Bloco2(Bloco): 
    def __init__(self,screen,pos,score,fase):
        Bloco.__init__(self,screen,pos,fase)
        self.img = resource.img_bl3
        self.batidasRestantes = 2
	self.score = score
	
    #rotina de tratamento da batida da bola
    def trata_batida(self,bola):
	self.score.add(15)
        self.batidasRestantes = self.batidasRestantes - 1
        if (self.batidasRestantes == 1):
            #se bater 1 vez, troca a imagem do bloco
            self.img = resource.img_bl4
        elif (self.batidasRestantes == 0):
            #se bater a segunda vez, destroi o bloco
            self.destroi()

###
#Controle da fase do jogo
###	    
class Fase(object):
    def __init__(self,screen, bola,arquivo_fase,score):
        self.blocos = []
        self.screen = screen
        self.bola = bola
	#Carrega o arquivo que define a fase
        arq = Arquivo()
        dados = arq.abrir(arquivo_fase)
        yps = 0
        dados = dados.replace("\n","")
        dados = dados.replace("\r","")
        dados = dados.replace("\t","")
        dados = dados.replace("\32","")
	#Monta os blocos na tela de acordo como descrito no arquivo
        if(dados.isdigit()):
            for i in range(1,len(dados)):
                item = dados[i:i+1]
                bl = int(item)
                if((i%20)==0):
                    yps+=1
                if(bl<3):
                    x = 139+(i%20)*37
                    y = 154+yps*12
                    if(bl==0):
                        tBloco = Bloco0(screen,(x,y),score,self)
                    else:
                        if(bl==1):
                            tBloco = Bloco1(screen,(x,y),score,self)

                        else:
                            if(bl==2):
                                tBloco = Bloco2(screen,(x,y),score,self)

                            else:
                                tBloco = Bloco0(screen,(x,y),score,self)

                    self.blocos.append(tBloco)
        else:
            print "Falha na leitura da fase, informacoes invalidas."

    #Pergunta para cada bloco se a bola bateu nele
    def bateu(self):
        for b in self.blocos:
            if(b.bateu(self.bola)):
                break

    #Retira um bloco da lista
    def remover_bloco(self,bloco):
	self.blocos.remove(bloco)
    
    #Verifica se o vetor de blocos está vazio
    def taVazio(self):
        return len(self.blocos)==0

    #Destroi o vetor de blocos
    def destroi(self):
        self.blocos = ""

    #Desenha os blocos na tela
    def draw(self):
        for b in self.blocos:
	    b.draw()
            
###
#Controla a barra do jogador        
###
class Barra(object):
    img = resource.img_barra
    
    def __init__(self,screen,jogo,bola):
        self.screen=screen
        self.jogo=jogo
        self.bola=bola
        self.img = resource.img_barra
        self.img_rect = self.img.get_rect()

        self.x=450
        self.y=725

        self.batida=False

    #Caso o usuário pressione as teclas de controle, atua com a ação correspondente
    def mover(self,key):
        if(key == K_LEFT):
            self.x-=10
        else:
            if(key == K_RIGHT):
                self.x+=10

        if(self.x<128):
            self.x = 129
        else:
            if((self.x+125)>896):
                self.x=771 #896-115

        if(not self.bola.estaRodando()):
            self.bola.movimentar(self.x)

    #Checa se a bola bateu na barra
    def bateu(self):
        bola_rect = self.bola.getRect()
        img_rect = self.img_rect.move(self.x,self.y)

        if(img_rect.colliderect(bola_rect) and not self.batida):
            self.bola.rebater(self.x)
            self.batida=True
        else:
            self.batida=False

    #Desenha a barra
    def draw(self):
        self.screen.blit(self.img,(self.x,self.y))

###
#A Bola do jogo
###	
class Bola(object):

    ballSpeed = 7
    img = resource.img_bola
    img_rect = img.get_rect()
    comecou = False

    x=469
    y=699
    ca=1
    cl=5
    inc=2
    
    def __init__(self,screen,jogo):
        self.screen = screen
        self.jogo = jogo
        #calculo do coeficiente linear
        self.cl = self.y - self.ca * self.x

    #Método para a rebatida ao lado de objetos
    def vertical(self):
	self.ca = math.pi - self.ca

    #Método para rebatida sobre e sob os objetos
    def horizontal(self):
        #reflexao da funcao
	self.ca = 2*math.pi - self.ca

    #Método para alteração do ângulo, específico na batida na barra
    def rebater(self,x):
        x = self.x - x
        #angulo de reflexao corresponde ao ponto de batida na barra ( -10 = 130 ateh 125 = 50)
	#angulo = 130 - ((((x+10)*80)/130)+50)
	#angulo = (math.round((x+10)/130.0)*80)+50 
	#angulo = 150 - ((((x+10)*80)/150)+30) 
	angulo = 130 - (((x+10)*80)/130)
	#tangente do valor corresponde ao coeficiente angular, *-1 para reflexao
        self.ca = (2*math.pi) - math.radians(angulo)
	print x, angulo, self.ca

    #Move a bola
    def mover(self):
        self.comecou=True
        dx = self.ballSpeed*math.cos(self.ca)
        dy = self.ballSpeed*math.sin(self.ca)
        self.x+=dx
        self.y+=dy

    #Altera a posição da bola enquanto o jogo não começou
    def movimentar(self,x):
        if(x<6):
            x=6
        if(x>774):
            x=774
        self.x=x

    #Aumenta a velocidade da bola
    def incSpeed(self):
        if(self.ballSpeed<12):
            self.ballSpeed+=self.inc

    #Posiciona a bola
    def setXY(self,x,y):
        self.x=x
        self.y=y

    #Retorna a posição atual da bola
    def getXY(self):
        return (self.x,self.y)

    #Desenha a bola
    def draw(self):
        self.screen.blit(self.img,(self.x,self.y))

    #Checa se a bola está em movimento
    def estaRodando(self):
        return self.comecou

    #Retorna o bounding box da bola
    def getRect(self):
        return self.img_rect.move(self.x,self.y)

###
#Controle de pontuação
###
class Pontuacao(object):
    def __init__(self,screen):
	self.screen = screen
	self.font = pygame.font.Font(resource.fonte,28)
	self.pontos = 0
    
    #Incrementa pontos
    def add(self,valor):
	self.pontos += valor
    
    #Remove Pontos
    def sub(self,valor):
	self.pontos -= valor
    
    #Desenha os pontos na tela
    def draw(self):
	text = self.font.render(("Pontos"),True,(255,255,255),(160,106,70))
	textRect = text.get_rect()
	textRect.centerx = 63 
	textRect.centery = 486
	self.screen.blit(text,textRect)
	text = self.font.render((str(self.pontos)),True,(255,255,255),(160,106,70))
	textRect = text.get_rect()
	textRect.centerx = 63
	textRect.centery = 520
	self.screen.blit(text,textRect)	

###
#Controle do Jogo
###
class Jogo(object):

    def __init__(self,screen):
        self.screen = screen
	self.font = pygame.font.Font(resource.fonte,28)
        self.bola = Bola(self.screen,self)
        self.barra = Barra(self.screen,self,self.bola)
	self.score = Pontuacao(self.screen)
        self.fase = Fase(self.screen,self.bola,resource.arquivo_fase,self.score)
        self.area = Area(self.screen,self.bola)
        self.barraLeft = False
        self.barraRight = False

        self.tempoInicial = int(time.time())

    def handle_events(self,gameloop):
        for event in pygame.event.get():
            if (event.type == KEYDOWN):
                if(event.key == K_ESCAPE):
                    gameloop.back_to_menu()

                if(event.key == K_LEFT):
                    self.barraLeft = True
                    self.barra_key = event.key
                elif(event.key == K_RIGHT):
                    self.barraRight = True
                    self.barra_key = event.key
                elif(event.key == K_SPACE):
                    self.bola.mover()
            elif(event.type == KEYUP):
                if(event.key == K_LEFT):
                    self.barraLeft = False
                elif(event.key == K_RIGHT):
                    self.barraRight = False

    def draw(self):
        self.screen.fill((228,171,135))
        self.bola.draw()
        self.barra.draw()
        self.fase.draw()
        self.area.draw()
        tempoFinal = int(time.time())
	tempo = tempoFinal-self.tempoInicial
	minutos = str(tempo/60).zfill(2)
	segundos = str(tempo%60).zfill(2)
	text = self.font.render((minutos+":"+segundos),True,(255,255,255),(160,106,70))
	textRect = text.get_rect()
	textRect.topleft = (927,486)
	self.screen.blit(text,textRect)
	self.score.draw()

    def step(self,gameloop):
        if(self.barraLeft or self.barraRight):
            self.barra.mover(self.barra_key)

        if(self.bola.estaRodando()):
            self.bola.mover()
            self.barra.bateu()
            self.fase.bateu()
            if(not self.area.bateu()):
		gameloop.back_to_menu()
	
	if(self.fase.taVazio()):
	    gameloop.back_to_menu()

###
#Menu do jogo
###
class Menu(object):

    def __init__(self,screen):
        
	self.screen = screen
        self.btJogo = pygame.Rect(357,220,341,94)

        self.btSair = pygame.Rect(357,502,341,94)
        self.telaMenu = resource.img_tela_menu

    def step(self,gameloop):
        pass

    def handle_events(self,gameloop):
        for event in pygame.event.get():
            if (event.type == MOUSEBUTTONDOWN):
                if (self.btJogo.collidepoint(event.pos[0],event.pos[1])):
		    gameloop.nova_tela(Jogo(self.screen))

                elif (self.btSair.collidepoint(event.pos[0],event.pos[1])):
                    gameloop.sair()

    def draw(self):
        self.screen.blit(self.telaMenu,(0,0))

	
###
#Loop do sistema, controle geral
###
class GameLoop(object):
    def __init__(self):
	pygame.init()
        #self.screen = pygame.display.set_mode( (1024,768), FULLSCREEN )
	self.screen = pygame.display.set_mode( (1024,768), pygame.DOUBLEBUF )

        pygame.mouse.set_visible( True )
        pygame.display.set_caption("Quebra Parede")

        self.run = True
	self.menu = Menu(self.screen)
	self.objeto=self.menu
	
	self.clock = pygame.time.Clock()
    
    #Volta para a tela do menu
    def back_to_menu(self):
	self.objeto = self.menu
	
    #Executa o loop eterno do sistema
    def loop(self):
	while (self.run):
	    self.objeto.handle_events(self)
	    self.objeto.step(self)
	    self.objeto.draw()
           
            pygame.display.flip()
	    self.clock.tick(40)
    
    #Sai do loop
    def sair(self):
	self.run=False;
    
    #Coloca outro objeto como tela atual
    def nova_tela(self,tela):
	self.objeto = tela

	

#########################    
gl = GameLoop()
gl.loop()