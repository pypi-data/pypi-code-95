import math
import time
import pygame
import pygame.draw
from pgzero import game, loaders
from pgzero.actor import ANCHOR_CENTER, POS_TOPLEFT, Actor, transform_anchor


class Actor(Actor):

    def __init__(self, image, pos=POS_TOPLEFT, anchor=ANCHOR_CENTER, **kwargs):
        '新的角色类'
        self._flip_x = False
        self._flip_y = False
        self._scale = 1
        self._mask = None
        self._taskid = 0
        self._animate_counter = 0  # 切换造型动画的计数
        self._images = [image]
        self.animate_fps = 10  # 切换造型的频率，默认是10，表示1s切换10次
        self.is_animate = 1
        self.maxfps = 120  # 角色响应任务事件的最大帧率，创建任务的时候每s可以有120个间隔来执行任务
        self.direction = 0
        self.tasks = {}
        super().__init__(image, pos, anchor, **kwargs)

    def distance_to(self, actor):
        '计算到另一个角色的距离'
        dx = actor.x - self.x
        dy = actor.y - self.y
        return math.sqrt(dx**2 + dy**2)

    def direction_to(self, actor):
        '计算面向另一个角色的方向'
        dx = actor.x - self.x
        dy = self.y - actor.y

        angle = math.degrees(math.atan2(dy, dx))
        if angle > 0:
            return angle

        return 360 + angle

    def move_towards(self, actor, dist):
        '朝另一个角色移动dist步'
        angle = math.radians(self.direction_to(actor))
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def point_towards(self, actor):
        '面向另一个角色'
        print(self.direction_to(actor))
        self.angle = self.direction_to(actor)

    def move_in_direction(self, dist):
        '朝着当前方向移动dist步，不是角色角度'
        angle = math.radians(self.direction)
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def move_forward(self, dist):
        '演着角色角度移动dist步'
        angle = math.radians(self.angle)
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def move_left(self, dist):
        '朝当前角度的左边移动dist步'
        angle = math.radians(self.angle + 90)
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def move_right(self, dist):
        '朝当前角度的右边移动dist步'
        angle = math.radians(self.angle - 90)
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    def move_back(self, dist):
        '倒退dist步'
        angle = math.radians(self.angle)
        dx = -dist * math.cos(angle)
        dy = -dist * math.sin(angle)
        self.x += dx
        self.y -= dy

    @property
    def images(self):
        '设置造型列表'
        return self._images

    @images.setter
    def images(self, images):
        '设置造型列表'
        self._images = images
        if len(self._images) != 0:
            self.image = self._images[0]

    def next_image(self):
        '下一个造型'
        if self.image in self._images:
            current = self._images.index(self.image)
            if current == len(self._images) - 1:
                self.image = self._images[0]
            else:
                self.image = self._images[current + 1]
        else:
            self.image = self._images[0]

    def toggle_animate(self):
        '切换角色是否自动切换造型'
        if self.is_animate:
            self.is_animate = 0
        else:
            self.is_animate = 1

    def animate(self):
        '''
        切换造型动画
        self.animate_fps为切换的频率，默认是10，表示1s切换10次
        '''
        if self.is_animate:
            if self.animate_fps < 0:
                self.animate_fps = 0
            now = int(time.time() * self.animate_fps)
            if now != self._animate_counter:
                self._animate_counter = now
                self.next_image()

    def run_tasks(self):
        '''
        根据计划任务执行要做的事
        需要放在update函数中执行
        '''
        self.animate()
        now = int(time.time() * self.maxfps)  # 获取当前绝对帧数
        # 如果任务过期就执行并删除
        for taskCounter in list(self.tasks):
            if taskCounter <= now:
                for taskid in self.tasks[taskCounter]:
                    self.tasks[taskCounter][taskid]()
                    # print(f'任务{taskid}执行完毕')
                del self.tasks[taskCounter]
            else:
                break

    def create_delay_tasks(self, task, seconds=1, times=1):
        '''
        创建任务队列并添加到角色的任务列表中。  
        延迟seconds秒执行task任务，times代表这个任务执行多少次
        不写第二个和第三个参数就是等待1秒执行1次task
        '''
        now = time.time()
        tasks = []
        for i in range(times):
            taskTime = now+(i+1)*seconds  # 计算执行任务的时间
            taskCounter = int(taskTime*self.maxfps)  # 计算计数器走到哪一帧
            self._taskid += 1
            # 将任务加到任务队列
            if taskCounter in self.tasks:
                self.tasks[taskCounter][self._taskid] = task
            else:
                self.tasks[taskCounter] = {self._taskid: task}
            tasks.append(self._taskid)  # 将任务加到任务列表用于返回
        return tasks

    def remove_taskById(self, id):
        '根据id删掉任务'
        index = None
        for i in self.tasks:
            if id in self.tasks[i]:
                del self.tasks[i][id]
                # print(f'任务{id}被取消')
                break

    @property
    def angle(self):
        '设置角度'
        return self._angle

    @angle.setter
    def angle(self, angle):
        '设置角度'
        self._angle = angle
        self._transform_surf()

    @property
    def scale(self):
        '设置缩放'
        return self._scale

    @scale.setter
    def scale(self, scale):
        '设置缩放'
        self._scale = scale
        self._transform_surf()

    @property
    def flip_x(self):
        '设置x方向翻转'
        return self._flip_x

    @flip_x.setter
    def flip_x(self, flip_x):
        '设置x方向翻转'
        self._flip_x = flip_x
        self._transform_surf()

    @property
    def flip_y(self):
        '设置x方向翻转'
        return self._flip_y

    @flip_y.setter
    def flip_y(self, flip_y):
        '设置y方向翻转'
        self._flip_y = flip_y
        self._transform_surf()

    @property
    def image(self):
        '设置造型'
        return self._image_name

    @image.setter
    def image(self, image):
        '设置当前造型'
        self._image_name = image
        self._orig_surf = self._surf = loaders.images.load(image)
        self._update_pos()
        self._transform_surf()

    def _transform_surf(self):
        '变换角色的缩放、翻转等'
        self._surf = self._orig_surf
        p = self.pos

        if self._scale != 1:
            size = self._orig_surf.get_size()
            self._surf = pygame.transform.scale(
                self._surf, (int(size[0] * self.scale), int(size[1] * self.scale)))
        if self._flip_x:
            self._surf = pygame.transform.flip(self._surf, True, False)
        if self._flip_y:
            self._surf = pygame.transform.flip(self._surf, False, True)

        self._surf = pygame.transform.rotate(self._surf, self._angle)

        self.width, self.height = self._surf.get_size()
        w, h = self._orig_surf.get_size()
        ax, ay = self._untransformed_anchor
        anchor = transform_anchor(ax, ay, w, h, self._angle)
        self._anchor = (anchor[0] * self.scale, anchor[1] * self.scale)

        self.pos = p
        self._mask = None

    def collidepoint_pixel(self, x, y=0):
        '检测碰撞到某个像素，像素级精确检测'
        if isinstance(x, tuple):
            y = x[1]
            x = x[0]
        if self._mask == None:
            self._mask = pygame.mask.from_surface(self._surf)

        xoffset = int(x - self.left)
        yoffset = int(y - self.top)
        if xoffset < 0 or yoffset < 0:
            return 0

        width, height = self._mask.get_size()
        if xoffset > width or yoffset > height:
            return 0

        return self._mask.get_at((xoffset, yoffset))

    def collide_pixel(self, actor):
        '检测碰撞其他某个角色，返回重叠的坐标，如果没重叠就直接返回None，像素级精确检测'
        for a in [self, actor]:
            if a._mask == None:
                a._mask = pygame.mask.from_surface(a._surf)

        xoffset = int(actor.left - self.left)
        yoffset = int(actor.top - self.top)

        return self._mask.overlap(actor._mask, (xoffset, yoffset))

    def collidelist_pixel(self, actors):
        '检测碰撞角色列表，返回碰撞到的角色的索引，没碰到返回None，像素级精确检测'
        for i in range(len(actors)):
            if self.collide_pixel(actors[i]):
                return i
        return None

    def collidelistall_pixel(self, actors):
        '检测碰撞角色列表，返回值是碰撞到的角色，返回一个列表，如果列表为空说明没碰到，像素级精确检测'
        collided = []
        for i in range(len(actors)):
            if self.collide_pixel(actors[i]):
                collided.append(i)
        return collided

    def obb_collidepoints(self, actors):
        '检测多个角色碰撞，旋转了rect，使得rect贴合角色'
        angle = math.radians(self._angle)
        costheta = math.cos(angle)
        sintheta = math.sin(angle)
        width, height = self._orig_surf.get_size()
        half_width = width / 2
        half_height = height / 2

        i = 0
        for actor in actors:
            tx = actor.x - self.x
            ty = actor.y - self.y
            rx = tx * costheta - ty * sintheta
            ry = ty * costheta + tx * sintheta

            if rx > -half_width and rx < half_width and ry > -half_height and ry < half_height:
                return i
            i += 1

        return -1

    def obb_collidepoint(self, x, y=0):
        '检测碰撞一个点，旋转了rect，使得rect贴合角色'
        if isinstance(x, tuple):
            y = x[1]
            x = x[0]
        angle = math.radians(self._angle)
        costheta = math.cos(angle)
        sintheta = math.sin(angle)
        width, height = self._orig_surf.get_size()
        half_width = width / 2
        half_height = height / 2

        tx = x - self.x
        ty = y - self.y
        rx = tx * costheta - ty * sintheta
        ry = ty * costheta + tx * sintheta

        if rx > -half_width and rx < half_width and ry > -half_height and ry < half_height:
            return True

        return False

    def circle_collidepoints(self, radius, actors):
        '检测碰撞一堆点，将角色变成圆形区域，适合于圆形角色的碰撞检测'
        rSquare = radius ** 2

        i = 0
        for actor in actors:
            dSquare = (actor.x - self.x)**2 + (actor.y - self.y)**2

            if dSquare < rSquare:
                return i
            i += 1

        return -1

    def circle_collidepoint(self, radius, x, y=0):
        '检测碰撞一个点，将角色变成圆形区域，适合于圆形角色的碰撞检测'
        if isinstance(x, tuple):
            y = x[1]
            x = x[0]
        rSquare = radius ** 2
        dSquare = (x - self.x)**2 + (y - self.y)**2

        if dSquare < rSquare:
            return True

        return False

    def draw(self):
        '绘图'
        game.screen.blit(self._surf, self.topleft)

    def get_rect(self):
        '获取角色的rect'
        return self._rect
