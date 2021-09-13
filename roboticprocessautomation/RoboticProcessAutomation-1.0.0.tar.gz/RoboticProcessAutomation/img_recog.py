from pyautogui import locateOnScreen, click, doubleClick, rightClick
import time
from pyscreeze import Box


def click_img(  target: str,
                target_region: tuple = (),
                target_confidence: float = 0.98,
                target_retries: int = 1,
                click_type: str = 'single',
                off_x: int = 0, 
                off_y: int = 0,
                mode: str = "E",
                wait_before_retry: int = 1,
                click_before_retry: tuple = ()
                ):
    '''
    This function is to click provided img (visible on the screen).

    Args:
        target: (str) - path to the img.
        target_region: (tuple) - img region rectangle in [pixels] (x,y,width,height)
        target_confidence: (float) - treshold for img recognition, 0.01 - ultra low 0.99 - high
        target_retries: (int) - how many retries would be performed for click img
        click_type: (str) - supported ones: single,double,right
        off_x: (int) - x axis offset applied to click action, from center of the target img 
        off_y: (int) - y axis offset applied to click action, from center of the target img 
        mode: (str) - F -> return False 
                      E -> return Exception /default/
        wait_before_retry: (int) - how long it would wait until each retry.
        click_before_retry: (tuple) - (x,y) to focus before retry
    Returns:
        (bool/Exception) - depends on Arg:mode
    '''
    t_reg = None if target_region == () else target_region
    for _ in range(target_retries):          
        img_rect = locateOnScreen(  target, 
                                    region = t_reg, 
                                    confidence = target_confidence, 
                                    grayscale=True
                                    ) 
        if img_rect!= None:
            mouse_click(img_rect,click_type,off_x,off_y)
            return True
        if wait_before_retry >= 1: 
            time.sleep(wait_before_retry)
        if click_before_retry != ():
            click(click_before_retry)
    else:
        print(f'{target} FAIL')
        if mode == "F": 
            return False
        raise Exception


def wait_img_appear(target: str,
                        target_region: tuple = None,
                        target_confidence: float = 0.98,
                        timeout: float = 120,
                        mode: str = "E"
                        ):
    """
    This function is to wait until provided img will appear on the screen.

    Args:
        target: (str) - path to the img.
        target_region: (tuple) - img region rectangle in [pixels] (x,y,width,height)
        target_confidence: (float) - treshold for img recognition, 0.01 - ultra low 0.99 - high
        timeout: (int) - how long it would wait for apperance [seconds] 
        mode: (str) - F -> return False 
                      E -> return Exception /default/
    Returns:
        (bool/Exception) - depends on arg:mode
    """
    t_reg = None if target_region == () else target_region
    for _ in range(timeout):
        if locateOnScreen(  target, 
                            region = t_reg, 
                            confidence = target_confidence,
                            grayscale = True
                            ) != None: 
            return True
        time.sleep(0.9)        
    else:
        if mode=="F":
            return False
        raise Exception   


def wait_img_disappear(target: str,
                          target_region: tuple = None,
                          target_confidence: float = 0.98,
                          timeout: float = 120,
                          mode: str = "E"
                          ):

    """
    This function is to wait until provided img will disappear from the screen.

    Args:
        target: (str) - path to the img.
        target_region: (tuple) - img region rectangle in [pixels] (x,y,width,height)
        target_confidence: (float) - treshold for img recognition, 0.01 - ultra low 0.99 - high
        timeout: (int) - how long it would wait for disapperance [seconds] 
        mode: (str) - F -> return False 
                      E -> return Exception /default/
    Returns:
        (bool/Exception) - depends on arg:mode
    """
    t_reg = None if target_region == () else target_region
    for _ in range(timeout):
        if locateOnScreen(  target, 
                            region = t_reg, 
                            confidence = target_confidence,
                            grayscale = True
                            ) == None:
            return True 
        time.sleep(0.9)        
    else:
        if mode=="F": 
            return False
        raise Exception      


def click_img_2(target: str = None,
                target_region: tuple = None,
                target_confidence: float = 0.98,
                target_retries: int = 3,
                click_type: str = 'single',
                off_x: int = 0, 
                off_y: int = 0,
                mode: str = "E",
                wait_before_retry: int = 1,
                click_before_retry: tuple = (),
                check: str = None,
                check_mode: str = "A",
                check_region: tuple = None,
                check_wait_before: float= 0.5,
                check_retries: int = 1,
                check_timeout: int = 3,
                check_confidence: float = 0.98,
                ):
    '''
    This function is to click provided img (visible on the screen).
    And additionaly check for apperance/disapperane of another img.

    Args:
        target: (str) - path to the img.
        target_region: (tuple) - img region rectangle in [pixels] (x,y,width,height)
        target_confidence: (float) - treshold for img recognition, 0.01 - ultra low 0.99 - high
        target_retries: (int) - how many retries would be performed for click img
        click_type: (str) - supported ones: single,double,right
        off_x: (int) - x axis offset applied to click action, from center of the target img 
        off_y: (int) - y axis offset applied to click action, from center of the target img 
        mode: (str) - F -> return False 
                      E -> return Exception /default/
        wait_before_retry: (int) - how long it would wait until each retry.
        click_before_retry: (tuple) - (x,y) to focus before retry
        check: (str) - path to img it would test for (dis)apperance
        check_mode: (str) - A - apperance
                            D - disapperance
        check_region: (tuple) - img region rectangle in [pixels] (x,y,width,height)
        check_wait_before: (float) - how long it would wait until test
        check_retries: (int) - how many test retries would be performed each loop run
        check_timeout: (int) - to be passed into wait_img_a/d func 
        check_confidence: (float) - to be passed into wait_img_a/d func 
    Returns:
        (bool/Exception) - depends on Arg:mode
    '''
    t_reg = None if target_region == () else target_region
    c_reg = None if check_region == () else check_region
    for _ in range(target_retries):          
        t_rect = locateOnScreen(target, 
                                region = t_reg, 
                                confidence = target_confidence, 
                                grayscale=True
                                ) 
        if t_rect!= None:
            mouse_click(t_rect,click_type,off_x,off_y)
            if check != None:
                for _ in range(check_retries):
                    time.sleep(check_wait_before)
                    if check_mode == "A":
                        if wait_img_appear( target = check,
                                                target_region= c_reg,
                                                target_confidence = check_confidence,
                                                timeout = check_timeout,
                                                mode = "F"
                                                ):
                            return True
                    if check_mode == "D":
                        if wait_img_disappear( target = check,
                                                target_region= c_reg,
                                                target_confidence = check_confidence,
                                                timeout = check_timeout,
                                                mode = "F"
                                                ):
                            return True
            else:
                return True
        if wait_before_retry >= 1: 
            time.sleep(wait_before_retry)
        if click_before_retry != ():
            click(click_before_retry)
    else:
        print(f'{target} FAIL')
        if mode == "F": 
            return False
        raise Exception


#####################################
# 1. Img Recognition HELPER FUNCTIONS
#####################################


def rect_center(target: Box) -> tuple:
    '''
    This function is to calculate center of an rectangle

    Args:
        target: (Box) - pyscreeze.Box
    Returns:
        (tuple) - s/e
    '''
    x = target.left + (target.width / 2)
    y = target.top + (target.height / 2)
    return (x, y)


def mouse_click(img_rect: Box, click_type: str, off_x: int, off_y: int):
    '''
    This function is to click on provided coordinates

    Args:
        img_rect: (Box) - pyscreeze.Box
        click_type: (str) - s/e
        off_x: (int) - s/e
        off_y: (int) - s/e
    '''
    x, y = rect_center(img_rect)
    if click_type == 'single':
        click(x + off_x, y + off_y)
    elif click_type == 'double':
        doubleClick(x + off_x, y + off_y)
    elif click_type == 'right':
        rightClick(x + off_x, y + off_y)
    else:
        raise ValueError('clickType not supported')