import asyncio
import websockets
import json


class ReversiLogic:
    def __init__(self):
        # 盤面に置かれているコマの種類 0 = なし 1 = 白 2 = 黒
        self.banmen_zyoutai = []

        for i in range(8):
            a = [0] * 8
            self.banmen_zyoutai.append(a)

        # 手番の色 1 = 白 2 = 黒
        self.teban = 2

        # 0 = 勝敗ついてない 1 = 白の勝ち 2 = 黒の勝ち 3 = 引き分け
        self.senkyou_jyoukyou = 0

        # オセロの最初の盤面
        self.banmen_zyoutai[3][3] = 1
        self.banmen_zyoutai[3][4] = 2
        self.banmen_zyoutai[4][3] = 2
        self.banmen_zyoutai[4][4] = 1

    def okeruka_hantei(self, zahyou_x, zahyou_y, teban, kaesu=True):
        """
        隣接したマス(8方向)に自分とは別の色があることを確認し、その先に自分と同じ色があるとtrueを返す関数

        args:
            zahyou_x(int):クリックしたx座標
            zahyou_y(int):クリックしたy座標
            teban(int):クリックした人の色

        Ruterns:
            Trueを返す
        """
        kaeshi = False

        print(zahyou_x, zahyou_y, teban)

        for rinsetsu_x in range(-1, 2):
            for rinsetsu_y in range(-1, 2):
                rinsetsu_zahyou_x = rinsetsu_x + zahyou_x
                rinsetsu_zahyou_y = rinsetsu_y + zahyou_y

                if (
                    0 <= rinsetsu_zahyou_x < 8
                    and 0 <= rinsetsu_zahyou_y < 8
                    and teban
                    != self.banmen_zyoutai[rinsetsu_zahyou_x][rinsetsu_zahyou_y]
                    and self.banmen_zyoutai[rinsetsu_zahyou_x][rinsetsu_zahyou_y] != 0
                ):
                    if self.iro_sikibetsu(
                        rinsetsu_zahyou_x,
                        rinsetsu_zahyou_y,
                        rinsetsu_x,
                        rinsetsu_y,
                        teban,
                        kaesu,
                    ):
                        kaeshi = True

        return kaeshi

    def iro_sikibetsu(self, ima_x, ima_y, rinsetsu_x, rinsetsu_y, teban, kaesu=True):
        """
        置こうとした場所に隣接する違う色のマスの先を再起して確認し、違う色があったらTrueを返す関数

        args:
            ima_x(int):照合したい場所のx座標
            ima_y(int):照合したい場所のy座標
            rinsetsu_x(int):照合したい方向へのx座標の向き(ベクトル的な)
            rinsetsu_y(int):照合したい方向へのy座標の向き(ベクトル的な)
            teban(int):自分の色

        Ruterns:
            マスの範囲外、クリックしたマスと同じマス以外ならば
            自分と違う色があったら次のマスを参照し、これを繰り返す
            参照した次のマスに自分と同じ色があったらTrueを返す
            なにもなかったらFalseを返す
        """

        print(ima_x, ima_y, rinsetsu_x, rinsetsu_y, teban)

        if 0 <= ima_x < 8 and 0 <= ima_y < 8 and (rinsetsu_x != 0 or rinsetsu_y != 0):
            if teban == self.banmen_zyoutai[ima_x][ima_y]:
                return True

            elif self.banmen_zyoutai[ima_x][ima_y] != 0:
                ziten_x = ima_x + rinsetsu_x
                ziten_y = ima_y + rinsetsu_y

                if self.iro_sikibetsu(
                    ziten_x,
                    ziten_y,
                    rinsetsu_x,
                    rinsetsu_y,
                    teban,
                    kaesu,
                ):
                    if kaesu:
                        self.banmen_zyoutai[ima_x][ima_y] = teban

                    return True

                else:
                    return False

            else:
                return False

        else:
            return False

    def banmen_seiri(self, teban):
        """
        盤面全部を参照しておけるかどうかを判定する

        arg:
            teban(int):自分の手番

        return:
            置ける場合Trueを返す
        """
        for i in range(8):
            for j in range(8):
                if self.banmen_zyoutai[i][j] == 0 and self.okeruka_hantei(
                    i, j, teban, False
                ):
                    return True

        return False

    def shouhai(self):
        """
        盤面を参照して勝敗を決める

        return:
            1 = 白の勝利
            2 = 黒の勝利
            3 = 引き分け
        """

        kazu_1 = 0
        kazu_2 = 0

        for i in range(8):
            for j in range(8):
                if self.banmen_zyoutai[i][j] == 1:
                    kazu_1 += 1
                elif self.banmen_zyoutai[i][j] == 2:
                    kazu_2 += 1

        if kazu_1 < kazu_2:
            return 2
        elif kazu_1 > kazu_2:
            return 1
        else:
            return 3

    def haichi(self, i, j):
        """
        コマを置いたあとに次の手番の人が置けるか判定してパスする

        arg:
            i(int):x座標
            j(int):y座標
        """
        if (
            0 <= i
            and i < 8
            and 0 <= j
            and j < 8
            and self.banmen_zyoutai[i][j] == 0
            and self.okeruka_hantei(i, j, self.teban)
        ):
            if self.teban == 1:
                self.banmen_zyoutai[i][j] = 1

                if self.banmen_seiri(2):
                    self.teban = 2

                elif not self.banmen_seiri(1):
                    self.senkyou_jyoukyou = self.shouhai()

            elif self.teban == 2:
                self.banmen_zyoutai[i][j] = 2

                if self.banmen_seiri(1):
                    self.teban = 1

                elif not self.banmen_seiri(2):
                    self.senkyou_jyoukyou = self.shouhai()


reversiLogic = ReversiLogic()

teban_kuro = None
teban_shiro = None


async def echo(websocket):
    global teban_kuro
    global teban_shiro
    if teban_kuro and not teban_shiro:
        teban_shiro = websocket
    if not teban_kuro and not teban_shiro:
        teban_kuro = websocket

    d = {
        "banmenzyoutai": reversiLogic.banmen_zyoutai,
        "teban": reversiLogic.teban,
        "shouhai": reversiLogic.senkyou_jyoukyou,
        "teban_color": None
    }

    if websocket == teban_kuro:
        d["teban_color"] = "teban_kuro"
    if websocket == teban_shiro:
        d["teban_color"] = "teban_shiro"

    s = json.dumps(d)
    await websocket.send(s)
    print("message")
    async for message in websocket:
        print(message)
        d = json.loads(message)
        if "haichi" in d:
            i = d["haichi"]["i"]
            j = d["haichi"]["j"]
            if reversiLogic.teban == 2 and websocket == teban_kuro:
                reversiLogic.haichi(i, j)
            if reversiLogic.teban == 1 and websocket == teban_shiro:
                reversiLogic.haichi(i, j)

            d = {
                "banmenzyoutai": reversiLogic.banmen_zyoutai,
                "teban": reversiLogic.teban,
                "shouhai": reversiLogic.senkyou_jyoukyou,
            }
            s = json.dumps(d)
            if teban_kuro:
                await teban_kuro.send(s)
            if teban_shiro:
               await teban_shiro.send(s)


async def main():
    async with websockets.serve(echo, "0.0.0.0", 39910):
        await asyncio.Future()


asyncio.run(main())
