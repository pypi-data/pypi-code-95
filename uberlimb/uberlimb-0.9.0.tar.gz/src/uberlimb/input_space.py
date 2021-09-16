import math

import numpy as np

from uberlimb.parameters import InputSpaceParams, PeriodicFunctionType


class InputSpace:
    def __init__(self,
                 params: InputSpaceParams,
                 mask: np.ndarray = None):
        self.params = params
        self.arr_x_resolution = round(params.x_resolution * params.resolution_factor)
        self.arr_y_resolution = round(params.y_resolution * params.resolution_factor)
        self.arr = self._create_input_array(mask)

    def _create_input_array(self,
                            mask: np.ndarray = None) -> np.ndarray:
        params = self.params
        SIZE_CONSTANT = 1920

        # basic init
        # we use `params.x_resolution` to determine the "coordinates" of the image
        # if we'll use `self.arr_x_resolution` instead, `params.resolution_factor`
        # will start zooming in/out when applied
        x = params.x_resolution * params.scale / SIZE_CONSTANT
        x = np.linspace(-x, x, self.arr_x_resolution)
        y = params.y_resolution * params.scale / SIZE_CONSTANT
        y = np.linspace(-y, y, self.arr_y_resolution)

        # offset
        if params.offset_x:
            x_offset = x.ptp() * params.offset_x / params.x_resolution
            x += x_offset
        if params.offset_y:
            y_offset = y.ptp() * params.offset_y / params.x_resolution
            y += y_offset

        x, y = np.meshgrid(x, y)

        # rotation
        if params.rotation:
            rot = params.rotation * np.pi / 180
            x_rot = np.cos(rot) * x + np.sin(rot) * y
            y_rot = np.cos(rot + np.pi / 2) * x + np.sin(rot + np.pi / 2) * y
            x, y = x_rot, y_rot

        # periodic function
        x, y = self._apply_periodic_function(x,
                                             y,
                                             params.periodic_function,
                                             params.per_factor,
                                             )

        x = x.reshape(-1, 1)
        y = y.reshape(-1, 1)

        # custom function
        if params.custom_function:
            f = eval(params.custom_function)
        else:
            f = np.sqrt(x ** 2 + y ** 2)

        alpha = np.full((x.size, 1), params.alpha)
        beta = np.full((x.size, 1), params.beta)

        # mask
        if mask is not None:
            z = (mask / mask.max()).reshape(-1, 1) * 2 - 1
        else:
            z = np.full((x.size, 1), 0)
        input_space = x, y, z, alpha, beta, f
        input_space = np.concatenate(np.array(input_space), axis=1)
        return input_space

    @staticmethod
    def _apply_periodic_function(x: np.ndarray,
                                 y: np.ndarray,
                                 function_type: PeriodicFunctionType,
                                 per_factor: float,
                                 ):
        x_temp = np.zeros_like(x)
        y_temp = np.zeros_like(y)
        for i in range(math.ceil(per_factor)):
            step_x, step_y = InputSpace._apply_periodic_step(x,
                                                             y,
                                                             function_type,
                                                             2 ** i,
                                                             )

            if i + 1 > per_factor:
                fract_factor = per_factor % 1
                step_x *= fract_factor ** 3
                step_y *= fract_factor ** 3
            x_temp += step_x
            y_temp += step_y
        x = x_temp / per_factor
        y = y_temp / per_factor
        return x, y

    '''
    1) создаем временные массивы из нулей такого же размера
    2) в цикле от 0 плюсуем туда периодик штуку с периодом
    2.1) если пер_фактор == 2.4, то результат 3го цикла умножаем на 0.4
    3) делим на пер фактор результат
    4) возвращаем как обычно
    '''

    @staticmethod
    def _apply_periodic_step(x: np.ndarray,
                             y: np.ndarray,
                             function_type: PeriodicFunctionType,
                             frequency_factor: float,
                             ):
        x, y = x * frequency_factor, y * frequency_factor
        if function_type == PeriodicFunctionType.DISABLED:
            pass
        elif function_type == PeriodicFunctionType.SIN:
            x, y = np.sin(x), np.sin(y)
        elif function_type == PeriodicFunctionType.TANG:
            x, y = np.tan(x), np.tan(y)
        elif function_type == PeriodicFunctionType.KVADRATIKI_S_RESHETKAMI:
            x, y = np.tan(x) + np.cos(x) + np.tan(5 * x), np.tan(y) + np.cos(y)
        elif function_type == PeriodicFunctionType.SECRET_FUNCTION1:
            x, y = 2 * np.tan(x) + np.sin(x), 3 * np.tan(y) + np.cos(y)
        elif function_type == PeriodicFunctionType.TILES_W_BUBBLES:
            x, y = np.tan(x) + np.cos(x) + 1 / np.tan(
                x), 1 / np.tan(y) + np.sin(y)
        elif function_type == PeriodicFunctionType.EXP:
            x, y = 0.7 * np.tan(4 * x) + 0.5 * np.cos(2 * x) + 1 / np.tan(
                3 * x), 1 / np.tan(4 * y) + 0.5 * np.sin(2 * y) + 0.6 * np.tan(3 * y)
        elif function_type == PeriodicFunctionType.EXP2:
            x, y = np.tan(x) + 0.8 * np.sin(x) + 0.7 / np.tan(x), 0.7 / np.tan(
                y) + 0.8 * np.sin(y) + np.tan(y)
        elif function_type == PeriodicFunctionType.EXP3:
            x, y = np.tan(0.4 * x) + np.sin(x) + 0.1 / np.tan(x), np.tan(
                0.4 * y) + 0.1 / np.tan(y) + np.sin(y)
        return x, y
