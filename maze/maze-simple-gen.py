# -*- coding: utf-8 -*-

import microbit as m
from random import randrange as rr
    
WW = 25
WH = 25
SW = 5
SH = 5

def clamp(a, b, c):
    return max(min(c, b), a)
            
class Game:
    def __init__(self):
        
        self.world = bytearray(WW * WH)
        self.player = [ 1, 1 ]
        self.pos = [0, 0]
        
        
    def getworld(self, x, y):
        return self.world[x + y * WW]
    
    def setworld(self, x, y, s):
        self.world[x + y * WW] = s
        
    def world2screen(self, p):
        return [ p[0] - self.pos[0], p[1] - self.pos[1] ]
    
    def screen2world(self, p):
        return [ p[0] + self.pos[0], p[1] + self.pos[1] ]
    
    def getscreen(self, x, y):
        p = self.screen2world((x, y))
        if p == self.player:
            return 9
        else:
            return self.getworld(p[0], p[1])
        
    def trymove1axis(self, p, d, axis):
        q = [ p[0], p[1] ]
        q[axis] += d
        limit = WW if axis == 0 else WH
        if q[axis] < 0 or q[axis] >= limit:
            return False, p
        if self.getworld(q[0], q[1]) != 0:
            return False, q
        return True, q

    def updatepos(self):
        self.pos[0] = clamp(0, self.player[0] - SW // 2, WW - SW)
        self.pos[1] = clamp(0, self.player[1] - SH // 2, WH - SH)
        

    #def moveplayer(self, dxy):
    def moveplayer(self, dxy, ax):
        for i in range(2):
            #if dxy[i] != 0:
            #    r, q = self.trymove1axis(self.player, dxy[i], i)
            if dxy[ax] != 0:
                r, q = self.trymove1axis(self.player, dxy[ax], ax)
                if r:
                    self.player = q
                    self.updatepos()
                    return True
            ax = 1 - ax
        return False
        


def mazelook(g, k):
    for x in range(1, WW - 1):
        for y in range(1, WH - 1):
            if g.getworld(x, y) == 4:
                if k == 0:
                    return x, y
                k -= 1
    return None, None

def mazeupd(g, x, y, active):
    p = g.getworld(x, y)
    if p == 4:
        g.setworld(x, y, 2)
        active -= 1
    elif p == 3:
        g.setworld(x, y, 4)
        active += 1
    
    return active
    

def maze(g):
    active = 0
    for x in range(WW):
        for y in range(WH):
            if x == 0 or y == 0 or x == WW - 1 or y == WH - 1:
                g.setworld(x, y, 2)
            else:
                g.setworld(x, y, 3)
                
    g.setworld(1, 1, 4)
    active += 1
    
    while active > 0:
        
        x, y = mazelook(g, rr(active))
        
        g.setworld(x, y, 0)
        active -= 1
        active = mazeupd(g, x - 1, y, active)
        active = mazeupd(g, x + 1, y, active)
        active = mazeupd(g, x, y + 1, active)
        active = mazeupd(g, x, y - 1, active)
    
    g.setworld(x, y, 8)
    return x, y

m.display.show(m.Image.CLOCK12)
g = Game()
gx, gy = maze(g)

f = 0    

while True:
    
    if m.button_a.is_pressed():
        m.display.clear()
        m.display.set_pixel(g.player[0] // 5, g.player[1] // 5, 9)
        m.display.set_pixel(gx * SW // WW, gy * SH // WH, 8 * (f % 2))
    else:
        
        for y in range(SW):
            for x in range(SW):
                v = g.getscreen(x, y)
                if v == 8 and f % 2 == 1:
                    v = 0
                m.display.set_pixel(x, y, v)
        
        dx = m.accelerometer.get_x()
        dy = m.accelerometer.get_y()
        ax = int(abs(dy) > abs(dx))
        dx = clamp(-1, dx // 200, 1)
        dy = clamp(-1, dy // 200, 1)
        if dx != 0 or dy != 0:
            g.moveplayer((dx, dy), ax)
            
        #dx = clamp(-1, m.accelerometer.get_x() // 200, 1)
        #dy = clamp(-1, m.accelerometer.get_y() // 200, 1)
        
        #g.moveplayer((dx, dy))

    m.sleep(200)
    f += 1
    if abs(g.player[0] - gx) + abs(g.player[1] - gy) <= 1:
        break

m.sleep(500)

while True:    
    m.display.scroll("{}s".format(f // 5))
    m.sleep(1000)
