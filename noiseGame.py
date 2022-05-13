from tkinter import *
from random import *
from time import sleep
from timeit import default_timer
from datetime import datetime


class CaveGenerator:
    
    def __init__(self,width,height,cell_size,noise_dens,iters):
        self.minvalue=0
        self.maxvalue=99
        self.noise_density=noise_dens
        self.iterations=iters

        self.cellsize=cell_size
        self.rows=int(height/cellsize)
        self.cols=int(width/cellsize)

        #generate empty tilemap
        self.tilemap=[]
        for i in range(self.rows):
            col=[]
            for j in range(self.cols):
                col.append(None)
            self.tilemap.append(col)
        
    #noise function
    ################################################################
    #assign each square a value
    def noise(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.tilemap[i][j]=randint(self.minvalue,self.maxvalue)

    #cellular automata
    ################################################################
    def cell_auto(self):
        for its in range(self.iterations):
            newtilemap=[]
            for i in range(self.rows):
                row=[]
                for j in range(self.cols):
                    value=self.maxvalue
                    wallneighbors=0
                    for n in range(i-1,i+2):
                        for m in range(j-1,j+2):
                            if self.is_in_map(m,n):
                                if n!=i or m!=j:
                                    if self.is_wall(m,n):
                                        wallneighbors+=1
                            else:
                                wallneighbors+=1
                    if wallneighbors > 4:
                        value=randint(self.minvalue,self.noise_density)
                    row.append(value)
                newtilemap.append(row)

            for i in range(self.rows):
                for j in range(self.cols):
                    self.tilemap[i][j]=newtilemap[i][j]


    #helper mathods
    ########################################################################
    #return bool of whether or not (x,y) is a valid space
    def is_in_map(self,x,y):
        return x>=0 and x<self.cols and y>=0 and y<self.rows

    def is_wall(self,x,y):
        return self.tilemap[y][x]<=self.noise_density


    #wrapper methods
    ########################################################################
    def generate(self):#keep
        self.noise()
        self.cell_auto()
        return self.tilemap



#map stuff
################################################################
root = Tk()#master runtime guy
root.title('Cave Game')

#map sizing stuff
w=800
h=500
cellsize=10
noise_density=57
iterations=6
cave_generator=CaveGenerator(w,h,cellsize,noise_density,iterations)
tilemap=cave_generator.generate()
changed=True

#boring gui stuff
canvas=Canvas(root, width=w, height=h, bg='white')
canvas.pack()

#make the character
#to reference the player's location: use tilemap[-1][0] for x, tilemap[-1][1]
#the indices of the first (50) lists and the indices of their values represent tilemap locations, while the values themselves represent wallvalue
#however the values of the last list represent the tilemap location of the player. weird i know
for i in range(len(tilemap)):
    over=False
    for j in range(len(tilemap[i])):
        if not cave_generator.is_wall(j,i):#place him somewhere that isn't a wall
            tilemap.append([j,i])
            over=True
            break
    if over:
        break

#generate money map
####################################################################
def find_hex_color(rgb):
    color='#'
    for i in rgb:
        ayo=hex(i)[2:]
        color+=f'{ayo:>2}'
    return color.replace(' ','0')

def generate_color(value, gradient):
    diff=cave_generator.maxvalue - cave_generator.minvalue
    r=value * int(gradient[0] / diff)
    g=value * int(gradient[1] / diff)
    b=value * int(gradient[2] / diff)
    return find_hex_color((r,g,b))

    
#draw the tilemap
####################################################################
player=canvas.create_rectangle(0,0,cellsize,cellsize,fill='blue')
    
def draw_tilemap():
    global changed
    if changed:
        #clear the canvas
        canvas.delete('all')
        
        #gridlines
        for i in range(0,w,cellsize):
            canvas.create_line(i,0,i,h,fill='gray')
        for i in range(0,h,cellsize):
            canvas.create_line(0,i,w,i,fill='gray')

        #tiles
        for i in range(len(tilemap))[:-1]:
            for j in range(len(tilemap[i])):
                if tilemap[i][j] <= noise_density:
                    x1=j*cellsize
                    y1=i*cellsize
                    x2=x1+cellsize
                    y2=y1+cellsize
                    
                    canvas.create_rectangle(x1,y1,x2,y2,fill=generate_color(tilemap[i][j],(255,255,0)))
        changed=False

        
    #player tile
    global player
    canvas.delete(player)
    x1=tilemap[-1][0]*cellsize
    y1=tilemap[-1][1]*cellsize
    x2=x1+cellsize
    y2=y1+cellsize
    player=canvas.create_rectangle(x1,y1,x2,y2,fill='blue')

    

#player actions
########################################################################
actions=[]

                    
def keyup(e):
    if  e.keysym in actions :
        actions.pop(actions.index(e.keysym))

def keydown(e):
    if not e.keysym in actions :
        actions.append(e.keysym)
        
def handle_actions():
    switch={'w':[0,-1],'s':[0,1],'a':[-1,0],'d':[1,0],'space':None}
    movenewx=tilemap[-1][0]
    movenewy=tilemap[-1][1]
    minenewx=tilemap[-1][0]
    minenewy=tilemap[-1][1]
    for char in actions:#gets the total prospect direction of movement
        if char in 'wasd':
            if cave_generator.is_in_map(movenewx+switch[char][0],movenewy+switch[char][1]) and not cave_generator.is_wall(movenewx+switch[char][0],movenewy+switch[char][1]):
                movenewx+=switch[char][0]
                movenewy+=switch[char][1]
            minenewx+=switch[char][0]
            minenewy+=switch[char][1]
    if 'space' in actions and cave_generator.is_in_map(minenewx,minenewy):
        mine_tile(minenewx,minenewy)
    move_player(movenewx,movenewy)
    
    
def move_player(newx,newy):
    if cave_generator.is_in_map(newx,newy) and not cave_generator.is_wall(newx,newy):
            tilemap[-1][0]=newx
            tilemap[-1][1]=newy
            

def mine_tile(col,row):
    if cave_generator.is_wall(col,row):
        tilemap[row][col]=cave_generator.maxvalue
        global changed
        changed=True
    
                
#do all the actions
########################################################################
draw_tilemap()
root.update()

root.bind('<KeyPress>', keydown)
root.bind('<KeyRelease>', keyup)
    
while True:
    #check player movement
    handle_actions()
    draw_tilemap()
    root.update()
    sleep(0.075)










