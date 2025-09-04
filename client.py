import asyncio
import sys
import json

import pygame
import websockets
from pygame.locals import *


class ReversiView:

    def __init__(self,reversilogic):
        pygame.init()  # Pygameを初期化
        self.screen = pygame.display.set_mode((400, 400))  # 画面を作成
        pygame.display.set_caption("リバーシ")  # タイトルを作成

        font1 = pygame.font.SysFont("hgｺﾞｼｯｸe", 30)

        self.taitoru = font1.render("リバーシ", True, (255, 255, 255))

        self.teban_shiro = font1.render("あなたは白です", True, (255, 255, 255))
        self.teban_kuro = font1.render("あなたは黒です", True, (0,0,0))

        self.siro_teban = font1.render("白の番です", True, (255, 255, 255))
        self.kuro_teban = font1.render("黒の番です", True, (0, 0, 0))

        self.siro_win = font1.render("白の勝ち", True, (255, 255, 255))
        self.kuro_win = font1.render("黒の勝ち", True, (0, 0, 0))
        self.hikiwake = font1.render("引き分け", True, (128, 0, 128))
        
        self.reversilogic = reversilogic
        self.run_mainloop()

    async def run_mainloop(self):
    
        while True:
            self.screen.fill((85,107,47)) 

            # 図形を描画
            for i in range(9):
                k = i * 40 + 40
                pygame.draw.line(self.screen,(255,255,255),(k,40),(k,360),2)
                pygame.draw.line(self.screen,(255,255,255),(40,k),(360,k),2)

            for i in range(8):

                for j in range(8):
                    k = i * 40 + 61
                    l = j * 40 + 61

                    if self.reversilogic.banmen_zyoutai[i][j] == 0:
                        pass

                    elif self.reversilogic.banmen_zyoutai[i][j] == 1:
                        pygame.draw.circle(self.screen,(255,255,255),(k,l), 15)    

                    elif self.reversilogic.banmen_zyoutai[i][j] == 2:   
                        pygame.draw.circle(self.screen,(0,0,0),(k,l), 15)

            if self.reversilogic.senkyou_jyoukyou == 0:
                if self.reversilogic.teban == 1: 
                    self.screen.blit(self.siro_teban, (245,365))
                elif self.reversilogic.teban == 2: 
                    self.screen.blit(self.kuro_teban, (245,365))
            
            elif self.reversilogic.senkyou_jyoukyou == 1:
                self.screen.blit(self.siro_win, (245,365))

            elif self.reversilogic.senkyou_jyoukyou == 2:
                self.screen.blit(self.kuro_win, (245,365))
            
            elif self.reversilogic.senkyou_jyoukyou == 3:
                self.screen.blit(self.hikiwake, (245,365))
            
            if self.reversilogic.teban_color == "teban_shiro":
                self.screen.blit(self.teban_shiro, (0,365))

            if self.reversilogic.teban_color == "teban_kuro":
                self.screen.blit(self.teban_kuro, (0,365))



                

            self.screen.blit(self.taitoru, (140,5))

            mouseX, mouseY = pygame.mouse.get_pos()

            pygame.display.update() #描画処理を実行

            for event in pygame.event.get():

                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    print("mouse clicked -> (" + str(x) + ", " + str(y) + ")")
                    i = (x - 40) // 40
                    j = (y - 40) // 40
                    print(i,j)

                    self.reversilogic.haichi(i,j)
            
                if event.type == pygame.QUIT:  # 終了イベント
                    pygame.quit()  #pygameのウィンドウを閉じる
                    sys.exit() #システム終了

            await asyncio.sleep(0.1)

class ReversiLogic:
    def __init__(self,websocket) -> None:
        self.websocket = websocket
        self.banmen_zyoutai = []

        for i in range(8):
            a = [0] * 8
            self.banmen_zyoutai.append(a)
        
        self.teban = 2
        self.senkyou_jyoukyou = 0
        self.teban_color = None

    def haichi(self,i,j):
        print("hi")
        d = {"haichi": {"i" : i ,"j" : j}}
        s = json.dumps(d)
        asyncio.ensure_future(self.websocket.send(s))
        
        

async def listen(websocket, reversilogic):
    async for message in websocket:
        print(message)
        d = json.loads(message)

        reversilogic.banmen_zyoutai = d["banmenzyoutai"]
        reversilogic.teban = d["teban"]
        reversilogic.senkyou_jyoukyou = d["shouhai"]
        if "teban_color" in d:
            reversilogic.teban_color = d["teban_color"]


async def main():
    uri = "ws://localhost:39910"
    async with websockets.connect(uri) as websocket:

        reversilogic = ReversiLogic(websocket)

        reversiview= ReversiView(reversilogic)

        task1 = asyncio.create_task(reversiview.run_mainloop())
        task2 = asyncio.create_task(listen(websocket, reversilogic))

        await task1
        task2.cancel()

        

asyncio.run(main())