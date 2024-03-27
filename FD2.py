# 导入必要的库
import pyautogui  # 用于自动化鼠标和键盘操作
import time  # 用于延迟和时间计算
import numpy as np  # 用于图像处理
import cv2  # OpenCV库，用于图像识别
import random  # 生成随机数，用于随机延迟
import ctypes  # 调用底层C库，这里用于模拟鼠标和键盘操作

# 全局变量定义
DEBUG = False  # 调试模式开关
info = 'init'  # 当前状态信息
mark = '+'  # 日志输出的标记符号
resRate = 1  # 图像分辨率缩放比例
opTime = time.time()  # 操作开始的时间
start_pos = None  # start按钮的位置
give_counter = 0  # 循环中的计数器，跟踪给予操作的次数
last_matched_pos = {}  # 初始化为空字典
she_click_time = time.time()  # 脚本开始时初始化


# Windows API常量定义，用于模拟鼠标操作
MOUSEEVENTF_MOVE = 0x0001  # 鼠标移动
MOUSEEVENTF_LEFTDOWN = 0x0002  # 鼠标左键按下
MOUSEEVENTF_LEFTUP = 0x0004  # 鼠标左键释放
MOUSEEVENTF_ABSOLUTE = 0x8000  # 绝对移动模式

def choose_mode():
    """选择模式函数"""
    global sheMode  # 声明全局变量sheMode
    while True:
        try:
            mode_input = input("请选择模式 (内射（不太推荐）：1, 同时（自行调节速度）：2, 外射（建议6速）：3): ")
            mode = int(mode_input)
            if mode in [1, 2, 3]:
                return mode
            else:
                print("无效的模式选择，请输入 1, 2, 或 3.")
        except ValueError:
            print("无效的输入，请输入一个数字 (1, 2, 3).")

def switchMark():
    """切换标记符号的函数"""
    global mark
    mark = '-' if mark == '+' else '+'

def log(buf):
    """输出日志信息的函数"""
    global info
    global mark
    global opTime
    if time.time() - opTime > 120:
        pyautogui.press('1')
        opTime = time.time()
    if buf != info:
        opTime = time.time()
        info = buf
        print(f'\n  {info}', end='')
    else:
        print(f'\r{mark}', end='')
        switchMark()

def match(template_name, ac=0.9):
    """图像匹配功能，寻找指定模板图像在屏幕中的位置"""
    global last_matched_pos
    img = pyautogui.screenshot()  # 获取当前屏幕截图
    open_cv_image = np.array(img)
    img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(f'./{template_name}.png', 0)
    x, y = template.shape[:2]
    template = cv2.resize(template, (int(y * resRate), int(x * resRate)))  # 调整模板大小
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val < ac:
        return None

    w, h = template.shape[::-1]
    match_center = (max_loc[0] + w // 2, max_loc[1] + h // 2)

    if template_name not in last_matched_pos or last_matched_pos[template_name] != match_center:
        print(f"模板 {template_name} 的匹配值: {max_val}, 新位置: {match_center}")
        last_matched_pos[template_name] = match_center

    return match_center




def start():
    """
    自动开始游戏的函数。
    尝试找到并点击“开始”按钮。
    """
    global start_pos
    pos = match('start')  # 查找开始按钮的位置
    if pos:
        print(f"start按钮的坐标: {pos}")
        start_pos = pos  # 记录start按钮的位置
        pyautogui.moveTo(pos[0], pos[1], duration=0.2)  # 移动鼠标到start按钮的位置
        pyautogui.click()  # 点击start按钮
        time.sleep(0.1)
    else:
        print("未找到start按钮。")

def ready_to_she():
    """
    准备进行施法操作的函数。
    根据所选模式匹配相应的“she”图标。
    """
    template_name = f'she{sheMode}'
    pos = match(template_name)
    if pos is not None:
        return pos
    else:
        print("等待发射")
        while True:
            time.sleep(0.5)
            pos = match(template_name)
            if pos is not None:
                return pos

def ready_to_start():
    """
    检查并返回“开始”按钮的位置。
    """
    return match('start')

def ready_to_finish():
    """
    检查并返回“结束”按钮的位置。
    """
    return match('finish')

def move_click_mouse(x, y):
    """
    使用ctypes模拟移动鼠标到(x, y)并点击。
    """
    x_scaled = int(x * 65535 / ctypes.windll.user32.GetSystemMetrics(0))
    y_scaled = int(y * 65535 / ctypes.windll.user32.GetSystemMetrics(1))
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, x_scaled, y_scaled, 0, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, x_scaled, y_scaled, 0, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, x_scaled, y_scaled, 0, 0)

def press_esc():
    """
    使用ctypes模拟按下ESC键。
    """
    VK_ESCAPE = 0x1B
    ctypes.windll.user32.keybd_event(VK_ESCAPE, 0, 0, 0)  # 按下ESC
    ctypes.windll.user32.keybd_event(VK_ESCAPE, 0, 2, 0)  # 释放ESC


# 施法操作函数
def she():
    """
    执行施法操作。
    包括寻找特定图标，移动鼠标并点击，以及多次按下ESC键。    
    """
    last_action_time = time.time()  # 初始化 last_action_time
    global she_click_time  # 记录上一次施法的时间
    print("正在尝试执行she函数...")

    # 定义一个内部函数来打印从上次操作到现在的时间间隔
    def print_action_interval(action="点击"):
        nonlocal last_action_time
        current_time = time.time()
        interval = current_time - last_action_time
        print(f"从上次{action}到现在的间隔时间：{interval:.3f}秒")
        last_action_time = current_time

    pos = match(f'she{sheMode}')
    if pos is None:
        print("未找到she图像，跳过此次操作。")
        return

    # 计算并应用随机偏移量
    offset_x = random.randint(-10, 10)
    offset_y = random.randint(-10, 10)
    new_pos = (pos[0] + offset_x, pos[1] + offset_y)
    print(f"移动并点击的位置: {new_pos}")
    move_click_mouse(new_pos[0], new_pos[1])  # 模拟鼠标移动并点击
    print_action_interval("点击")

    # 定义一个函数来执行多次按ESC键的操作，并在每次操作之间添加随机延迟
    def perform_action(action, intervals):
        for base_interval in intervals:
            interval = base_interval + random.uniform(-0.015, 0.015)
            time.sleep(interval)
            action()
            print("已按ESC")
            print_action_interval("按ESC")

    base_delays = [0.042, 0.042, 0.035, 0.049, 0.043]
    perform_action(press_esc, base_delays)  # 执行按ESC键操作
    she_click_time = time.time()
    pyautogui.moveRel(50 * resRate, 50 * resRate)  # 移开当前位置

def wait_until_finish_found():
    """
    循环等待直到“结束”按钮出现。
    """
    pos = ready_to_finish()
    while pos is None:
        log('首次等待后未找到结束，再等待2秒后重试')
        time.sleep(2)
        pos = ready_to_finish()
    finish()
    pyautogui.moveRel(50 * resRate, 50 * resRate)
    log('结束')

def finish():
    """
    执行结束游戏的操作。
    """
    print("开始点击结束")
    global she_click_time
    pos = ready_to_finish()
    if pos:
        print(f"finish按钮的坐标: {pos}")
        finish_click_time = time.time()
        interval = finish_click_time - she_click_time
        print(f"从点击she到点击finish的时间间隔是：{interval:.2f}秒")
        pyautogui.moveTo(pos[0], pos[1])
        pyautogui.leftClick()
        time.sleep(0.1)
        pyautogui.leftClick()

def after_give():
    """
    给予道具后的额外操作。
    """
    if sheMode in [1, 3] and start_pos:
        new_pos = (start_pos[0] + 50 * resRate, start_pos[1] + 50 * resRate)
        print(f"移动鼠标到位置: {new_pos}")
        pyautogui.moveTo(new_pos[0], new_pos[1], duration=0.2)

def give():
    """
    自动点赞功能实现。    
    """
    # 获取游戏窗口的位置
    win = pyautogui.getWindowsWithTitle('FallenDoll')[0]
    x, y = win.left, win.top

    print("开始点赞")
    # 定义需要点击的坐标列表，每个坐标对应一个操作
    click_positions = [
        (x + 339 * resRate, y + 280 * resRate + 35),  # 第一次点击的位置
        (x + 94 * resRate, y + 310 * resRate + 60)    # 第二次点击的位置
    ]

    # 第一次点击位置
    pyautogui.moveTo(*click_positions[0])
    pyautogui.click()
    time.sleep(0.1)

    # 移动到第二次点击的位置并执行多次点击
    pyautogui.moveTo(*click_positions[1])
    for _ in range(10):  # 假设需要点击7次
        pyautogui.click()
        time.sleep(0.05)



def initialize():
    # 尝试找到并点击开始
    start_pos = ready_to_start()
    if start_pos:
        start()
        pyautogui.moveRel(50 * resRate, 50 * resRate)
        log('点击开始')
    else:
        # 如果开始按钮不可用，尝试结束当前状态并重新开始
        finish_pos = ready_to_finish()
        if finish_pos:
            finish()
            pyautogui.moveRel(50 * resRate, 50 * resRate)
            log('结束')
            time.sleep(4)  # 等待一段时间以确保界面更新
            # 尝试再次点击开始
            if ready_to_start():
                start()
                pyautogui.moveRel(50 * resRate, 50 * resRate)
                log('点击开始')
            else:
                log('启动失败，未能找到开始按钮。')
                return False
    return True


def loop():
    global she_click_time, give_counter
    while True:
        # 等待she操作完成
        loop_start_time = time.time()  # 记录循环开始的时间
        while not ready_to_she():
            log('等待炮击')
            time.sleep(0.2)
        she()
        she_finish_time = time.time()
        she_duration = she_finish_time - loop_start_time
        print(f"从start到she完成，总共花费时间：{she_duration:.2f}秒")

        # 对于模式2，执行特定逻辑
        if sheMode == 4:
            wait_until_finish_found()  # 确保处理了finish
            time.sleep(3)  # 等待游戏状态更新，确保start按钮可点击
            if ready_to_start():  # 确认start按钮可点击
                start()
            else:
                log("未找到start按钮。等待中...")
                while not ready_to_start():
                    log('等待开始')
                    time.sleep(0.2)
                start()
        else:
            # 对于模式1和3，给系统一点反应时间并持续寻找finish和start
            time.sleep(2 * 1)
            while True:
                finish_found = ready_to_finish()
                start_found = ready_to_start()

                if finish_found:
                    # 如果找到finish按钮，先点击它
                    finish()
                    pyautogui.moveRel(50 * resRate, 50 * resRate)  # 移开当前位置以避免遮挡

                    # 给start按钮变为可点击的状态一点时间
                    time.sleep(2)
                    while not ready_to_start():
                        log('等待开始')
                        time.sleep(0.2)
                    start()
                    pyautogui.moveRel(50 * resRate, 50 * resRate)  # 再次移开当前位置
                    break  # 退出循环继续下一次

                elif start_found:
                    # 如果首先找到的是start按钮，直接点击它
                    time.sleep(1)
                    start()
                    pyautogui.moveRel(50 * resRate, 50 * resRate)  # 移开当前位置
                    break  # 退出循环继续下一次

                time.sleep(0.2)  # 没找到任何按钮，短暂等待后重试

        # 处理give逻辑
        give_cycle = 5 if sheMode in [1, 3] else 10
        if give_counter >= give_cycle - 1:
            give()
            after_give()
            give_counter = 0
        else:
            give_counter += 1

        interval = time.time() - she_click_time
        print(f"从点击she到下一次操作的时间间隔是：{interval:.2f}秒")






if __name__ == '__main__':
    sheMode = choose_mode()  # 在脚本开始时选择模式
    if initialize():  # 初始化
        loop()  # 进入主循环
    else:
        print("初始化失败，请检查游戏状态。")