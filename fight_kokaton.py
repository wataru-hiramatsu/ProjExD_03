import random
import sys
import time
import math

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ


class Character:
    def get_rct(self) -> pg.Rect:
        return self._rct


def check_bound(area: pg.Rect, obj: Character) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数1 area：画面SurfaceのRect
    引数2 obj：Characterクラス（爆弾，こうかとん）
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.get_rct().left < area.left or area.right < obj.get_rct().right:  # 横方向のはみ出し判定
        yoko = False
    if obj.get_rct().top < area.top or area.bottom < obj.get_rct().bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


class Bird(Character):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    _delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self._img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"ex03/fig/{num}.png"),
                0,
                2.0),
            True,
            False
        )
        self._rct = self._img.get_rect()
        self._rct.center = xy
        self._direction = (1, 0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self._img = pg.transform.rotozoom(
            pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self._img, self._rct)

    def get_direction(self) -> tuple[int, int]:
        return self._direction

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        direction_tmp = [0, 0]
        for k, mv in __class__._delta.items():
            if key_lst[k]:
                self._rct.move_ip(mv)
                direction_tmp[0] += mv[0]
                direction_tmp[1] += mv[1]
        if not (direction_tmp[0] == direction_tmp[1] == 0):
            self._direction = tuple(direction_tmp)
        if check_bound(screen.get_rect(), self) != (True, True):
            for k, mv in __class__._delta.items():
                if key_lst[k]:
                    self._rct.move_ip(-mv[0], -mv[1])
        screen.blit(self._img, self._rct)


class Beam(Character):
    def __init__(self, bird: Bird) -> None:
        self._direction = bird.get_direction()
        self._img = pg.transform.rotozoom(
            pg.image.load("ex03/fig/beam.png"),
            math.degrees(math.atan2(-self._direction[1], self._direction[0])),
            1)
        self._rct = self._img.get_rect()
        self._rct.center = bird.get_rct().midright

    def update(self, screen: pg.Surface) -> None:
        self._rct.move_ip(self._direction)
        screen.blit(self._img, self._rct)


class Bomb(Character):
    """
    爆弾に関するクラス
    """

    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self._img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self._img, color, (rad, rad), rad)
        self._img.set_colorkey((0, 0, 0))
        self._rct = self._img.get_rect()
        self._rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self._vx, self._vy = +1, +1

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(screen.get_rect(), self)
        if not yoko:
            self._vx *= -1
        if not tate:
            self._vy *= -1
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)


class Explosion:
    def __init__(self, pos: tuple[int, int]) -> None:
        self._imgs: list[pg.Surface] = []
        self._imgs.append(pg.image.load("ex03/fig/explosion.gif"))
        self._imgs.append(pg.transform.flip(self._imgs[0], True, True))

        self._rct = self._imgs[0].get_rect()
        self._rct.center = pos
        self._life = 100

    def update(self, screen: pg.Surface) -> None:
        screen.blit(self._imgs[self._life % len(self._imgs)], self._rct)
        self._life -= 1


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")

    bird = Bird(3, (900, 400))
    NUM_OF_BOMBS = 5
    bombs: list[Bomb] = []
    for _ in range(NUM_OF_BOMBS):
        bombs.append(
            Bomb(
                (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                ),
                random.randint(10, 50))
        )
    beam: Beam = None
    explosions: list[Explosion] = []

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        tmr += 1
        screen.blit(bg_img, [0, 0])

        if bird:
            for bomb in bombs:
                if bird.get_rct().colliderect(bomb.get_rct()):
                    # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return

        if beam and bird:
            for bomb in bombs:
                if beam.get_rct().colliderect(bomb.get_rct()):
                    explosions.append(Explosion(bomb.get_rct().center))
                    bombs.remove(bomb)
                    beam = None
                    break

        if len(bombs) <= 0:
            bird.change_img(6, screen)

        key_lst = pg.key.get_pressed()
        if key_lst[pg.K_SPACE]:
            beam = Beam(bird)

        if bird:
            bird.update(key_lst, screen)
        for bomb in bombs:
            bomb.update(screen)
        for explosion in explosions:
            explosion.update(screen)
            if explosion._life < 0:
                explosions.remove(explosion)
        if beam:
            beam.update(screen)

        pg.display.update()
        clock.tick(1000)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
