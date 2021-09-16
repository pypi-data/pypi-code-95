from abc import ABC

from uberlimb.input_space import InputSpace
from uberlimb.parameters import AnimationFunction
from uberlimb.renderer import Renderer
from uberlimb.video.animation import bernoulli_animation, animate_alpha_beta


class Animator(ABC):
    def __init__(self, renderer: Renderer):
        self.renderer = renderer

    def step_function(self) -> bool:
        return True


class BernoulliAnimator(Animator):
    @staticmethod
    def _create_input_generator(input_space: InputSpace,
                                num_frames: int,
                                copy_each_step=True):
        input_arr = input_space.arr.copy()
        alpha_beta = bernoulli_animation(alpha=input_space.params.alpha,
                                         beta=input_space.params.beta,
                                         num_frames=num_frames)
        for alpha, beta in alpha_beta:
            if copy_each_step:
                input_arr = input_space.arr.copy()
            input_arr[:, 3] = alpha
            input_arr[:, 4] = beta
            yield input_arr

    def __init__(self, renderer: Renderer):
        super().__init__(renderer)
        self.num_frames = round(self.renderer.params.animation.fps
                                * self.renderer.params.animation.length)
        self.generator = self._create_input_generator(self.renderer.input_space,
                                                      self.num_frames)
        self.frame_idx = 0

    def step_function(self) -> bool:
        if self.frame_idx >= self.num_frames:
            raise ValueError('Animation should be finished already')
        self.renderer.input_space.arr = next(self.generator)
        self.frame_idx += 1
        return self.frame_idx >= self.num_frames


class CircleAnimator(Animator):
    @staticmethod
    def _create_input_generator(input_space: InputSpace,
                                num_frames: int,
                                copy_each_step=True):
        if copy_each_step:
            input_space = None
        else:
            input_space = input_space.arr.copy()
        alpha_beta = animate_alpha_beta(alpha=input_space.params.alpha,
                                        beta=input_space.params.beta,
                                        num_frames=num_frames)
        for alpha, beta in alpha_beta:
            if copy_each_step:
                input_space = input_space.arr.copy()
            input_space[:, 3] = alpha
            input_space[:, 4] = beta
            yield input_space

    def __init__(self, renderer: Renderer):
        super().__init__(renderer)
        self.num_frames = round(self.renderer.params.animation.fps
                                * self.renderer.params.animation.length)
        self.generator = self._create_input_generator(self.renderer.input_space,
                                                      self.num_frames)
        self.frame_idx = 0

    def step_function(self) -> bool:
        if self.frame_idx >= self.num_frames:
            raise ValueError('Animation should be finished already')
        self.renderer.input_space.arr = next(self.generator)
        self.frame_idx += 1
        return self.frame_idx >= self.num_frames


animator_lookup = {
    AnimationFunction.BERNOULLI: BernoulliAnimator,
    AnimationFunction.DEFAULT: CircleAnimator,
}
