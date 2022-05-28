from tkinter import *
from random import *
from time import sleep
from PIL import Image, ImageTk
from datetime import datetime


class CaveGenerator:
    
    def __init__(self,width,height,cell_size,noise_dens,iters):
        self.minvalue=0#please make positive
        self.maxvalue=99#^^
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
        return self.tilemap[y][x] in range(0,self.noise_density+1)


    #wrapper methods
    ########################################################################
    def generate(self):#keep
        self.noise()
        self.cell_auto()
        return self.tilemap


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

#map stuff
################################################################
#initialization stuff
w=800
h=500
cellsize=10
noise_density=57
iterations=6

wall_color=(255,255,0)#red
ground_color=(167, 129, 68)#brownish
grid_color=find_hex_color((167, 129, 68))#brownish
gui_bg_color=find_hex_color((147,109,48))#darker brownish
money_color=find_hex_color((255,255,0))
transparent=find_hex_color((255,255,254))#reserved this to be seen as transparent

player_pos=None
money=0#the player's amount of cash money dolla beeohs
lives=3#player's lives duh
hurttime=datetime.now()
immunity=2#seconds the player should have immunity after being hit

enemies={'bill':[5,5]}

root = Tk()#master runtime guy
root.title('Cave Game')
root.configure(background=gui_bg_color)
root.wm_attributes('-transparentcolor',transparent)

cave_generator=CaveGenerator(w,h,cellsize,noise_density,iterations)
tilemap=cave_generator.generate()
changed=True


#boring gui stuff
############################################################################
money_label=Label(root,text=f'${money:>4}',fg=money_color,bg=gui_bg_color,font=('courier 40 bold'))

canvas=Canvas(root, width=w, height=h, bg=find_hex_color(ground_color),highlightthickness=0)

photo=PhotoImage(file='pheart.png')
photoimage=photo.subsample(10,10)

heartlabels=[]
for i in range(lives):
    heartlabels.append(Label(root,image=photoimage,background=gui_bg_color))
    heartlabels[-1].grid(row=0,column=1+i)

money_label.grid(row=0,column=0)
canvas.grid(row=1,column=0,columnspan=int(0.5*(w/cellsize)))



#place stuff in the map
###################################################################################
#place player
#to reference the player's location: use tilemap[-1][0] for x, tilemap[-1][1]
#the indices of the first (50) lists and the indices of their values represent tilemap locations, while the values themselves represent wallvalue
#however the values of the last list represent the tilemap location of the player. weird i know
def place_stuff():
    global player_pos
    global tilemap
    
    for i in range(len(tilemap)):
        over=False
        for j in range(len(tilemap[i])):
            if not cave_generator.is_wall(j,i):#place him somewhere that isn't a wall
                player_pos=[j,i]
                over=True
                break
        if over:
            break

    #place entry and exit
    #entry
    tilemap[player_pos[1]][player_pos[0]]=-1

    #exit
    for i in range(len(tilemap)-1,-1,-1):
        over=False
        for j in range(len(tilemap[i])-1,-1,-1):
            if not cave_generator.is_wall(j,i):
                tilemap[i][j]=-2
                over=True
                break
        if over:
            break
    
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
            canvas.create_line(i,0,i,h,fill=grid_color)
        for i in range(0,h,cellsize):
            canvas.create_line(0,i,w,i,fill=grid_color)

        #tiles
        for i in range(len(tilemap)):
            for j in range(len(tilemap[i])):
                x1=j*cellsize
                y1=i*cellsize
                x2=x1+cellsize
                y2=y1+cellsize
                color=None
                tile=False
                
                if tilemap[i][j] == -1:
                    color='pink'
                    tile=True
                elif tilemap[i][j] == -2:
                    color='pink'
                    tile=True
                elif tilemap[i][j] <= noise_density:
                    color=generate_color(tilemap[i][j],wall_color)
                    tile=True
                for k in enemies:
                    if enemies[k] == [j,i]:
                        color='red'
                        tile=True
                    
                if tile:
                    canvas.create_rectangle(x1,y1,x2,y2,fill=color)
        changed=False

        
    #player tile
    global player
    global player_pos
    canvas.delete(player)
    x1=player_pos[0]*cellsize
    y1=player_pos[1]*cellsize
    x2=x1+cellsize
    y2=y1+cellsize
    player=canvas.create_rectangle(x1,y1,x2,y2,fill='blue')

#game build stuff
#######################################################################
def next_level():
    global tilemap
    global changed
    
    tilemap=cave_generator.generate()
    changed=True
    place_stuff()

    sleep(1)
    

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
    global player_pos
    global hurttime
    global immunity

    #check player position for special stuff to do
    if tilemap[player_pos[1]][player_pos[0]] == -2:#if current space is the exit
        next_level()

    for k in enemies:
        if player_pos == enemies[k] and (datetime.now()-hurttime).total_seconds() > immunity:
            lose_health(1)
            hurttime=datetime.now()

    #move and mine
    switch={'w':[0,-1],'s':[0,1],'a':[-1,0],'d':[1,0],'space':None}
    movenewx=player_pos[0]
    movenewy=player_pos[1]
    minenewx=player_pos[0]
    minenewy=player_pos[1]
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
    global player_pos
    if cave_generator.is_in_map(newx,newy) and not cave_generator.is_wall(newx,newy):
        player_pos=[newx,newy]
            

def mine_tile(col,row):
    global changed
    global money
    if cave_generator.is_wall(col,row):
        money+=tilemap[row][col]
        money_label['text']=f'${money:>4}'
        tilemap[row][col]=cave_generator.maxvalue
        changed=True

def lose_health(amount):
    global lives
    if lives > 0:
        heartlabels[0].grid_forget()
        heartlabels.pop(0)
        lives-=amount
    else:
        print('you died play again?')
    
                
#do all the actions
########################################################################
place_stuff()
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










