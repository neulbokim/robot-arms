import pygame
import numpy as np

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (255,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (50,50,50)

FPS = 60 # frames per second

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

def Tmat(tx, ty):
    Translation = np.array( [
        [1,0,tx],
        [0,1,ty],
        [0,0,1]])
    return Translation

def Rmat(degree):
    rad = np.deg2rad(degree)
    c = np.cos(rad)
    s = np.sin(rad)
    R = np.array([
        [c,-s,0],
        [s,c,0],
        [0,0,1]])
    return R

def draw(P, H, screen, color = (100,200,200)):
    R = H[:2,:2]
    T = H[:2,2]
    Ptransformed = P @ R.T + T
    pygame.draw.polygon(screen, color = color,
                        points = Ptransformed, width = 3)
    

def main():
    pygame.init() # initialize the engine
    pygame.display.set_caption("20220042 김현서") #윈도우 제목
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    rect_w = 120
    rect_h = 40
    arm_w = rect_w
    arm_h = rect_h
    hand_w = arm_h
    hand_h = 0.2 * arm_h
    finger_w = 0.3 * hand_w
    finger_h = 3 * finger_w
    rectX = np.array([ [0,0],[rect_w,0],[rect_w,rect_h],[0,rect_h]])
    arm = np.array([[0,0],[arm_w,0],[arm_w,arm_h],[0,arm_h]])
    hand = np.array([[0,0],[hand_w,0],[hand_w,hand_h],[0,hand_h]])
    finger = np.array([[0,0],[finger_w,0],[finger_w,finger_h],[0,finger_h]])

    position = [(WINDOW_WIDTH/2)-(rect_w/2),WINDOW_HEIGHT-100]
    joint_angle1 = 10
    joint_angle2 = -30
    joint_angle_f1 = 0
    joint_angle_f2 = 0

    tick = 0
    v = 0
    tick_f1 = 0
    v_f1 = 0

    space = 0

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    space += 1
                    v_f1 = -1
                    if space % 2 == 0:
                        v_f1 = 1
                if event.key == pygame.K_LEFT:
                    v = -1
                elif event.key == pygame.K_RIGHT:
                    v = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    v = 0
                elif event.key == pygame.K_RIGHT:
                    v = 0

        angle_range = 50
        if -angle_range<=tick+v<=angle_range:
            tick += v
        else:
            v = 0

        if -50<=tick_f1+v_f1<=0:
            tick_f1 += v_f1
        else:
            v_f1 = 0
        
        #drawing
        screen.fill((255,200,200))

        #base: WHITE rectangle
        pygame.draw.circle(screen, RED, position, radius=3)
        base = Tmat(position[0],position[1]) @ Tmat(0,-rect_h)
        arm_base = Tmat(position[0], position[1])@Tmat(0,-arm_h)
        hand_base = Tmat(position[0],position[1])@Tmat(0,-hand_h)
        draw(rectX, base, screen, WHITE)

        # arm 1
        A1 = arm_base @ Tmat(arm_w/2, 0)
        x, y = A1[0,2], A1[1,2] #joint position
        pygame.draw.circle(screen, RED, (x,y), radius=3) #joint position
        A11 = A1 @ Rmat(-90) @ Tmat(0, -arm_h/2)
        # draw(rectX, H11, screen, YELLOW) # arm1, 90 degree
        joint_angle1 = angle_range * np.sin(np.deg2rad(tick))
        A12 = A11 @ Tmat(0,arm_h/2)@Rmat(joint_angle1)@Tmat(0,-arm_h/2)
        draw(arm, A12, screen, GREEN) # arm1 - 회전 조금

        # arm 2
        A2 = A12 @ Tmat(arm_w, 0) @ Tmat(0,arm_h/2) # joint 2
        x, y = A2[0,2], A2[1,2]
        pygame.draw.circle(screen, RED, (x,y), radius=3) # joint position
        joint_angle2 = angle_range * np.sin(np.deg2rad(tick))
        A21 = A2 @ Rmat(joint_angle2)@Tmat(0,-arm_h/2)
        draw(arm, A21, screen, BLUE)

        # arm 3
        A3 = A21 @ Tmat(arm_w, 0) @ Tmat(0, arm_h/2) #joint 3
        x, y = A3[0,2], A3[1,2]
        pygame.draw.circle(screen, RED, (x,y), radius = 3) #joint position
        joint_angle3 = angle_range * np.sin(np.deg2rad(tick))
        A31 = A3 @ Rmat(joint_angle3)@Tmat(0,-arm_h/2)
        draw(arm, A31, screen, YELLOW)

        # hand 1
        H1 = A31 @ Tmat(arm_w,0)@Tmat(0,arm_h/2)
        x, y = H1[0,2], H1[1,2]
        pygame.draw.circle(screen, RED, (x,y), radius = 3) #joint position
        H11 = H1 @ Rmat(-90) @ Tmat(0, hand_h/2) @ Tmat(-hand_w/2,0)
        # @ A31 @ Tmat(arm_w, 0) @ Tmat(0,arm_h)
        #joint_angle4 = angle_range * np.sin(np.deg2rad(tick))
        #H12 = H11 @ Rmat(joint_angle4)@Tmat(0,-hand_h/2)
        draw(hand, H11, screen, BLACK)

        # finger 1
        F1 = H11@Tmat(0,hand_h)@Tmat(finger_w/2,0)
        x, y = F1[0,2],F1[1,2]
        pygame.draw.circle(screen, RED, (x,y), radius=3) #joint position
        F11 = F1 @ Tmat(-finger_w/2,0)
        joint_angle_f1 = 30*np.sin(np.deg2rad(tick_f1))
        F12 = F11 @ Tmat(0,finger_h/2)@Rmat(joint_angle_f1)@Tmat(0,-finger_h/2)
        draw(finger, F12, screen, BLACK)

        # finger 2
        F2 = H11@Tmat(0,hand_h)@Tmat(hand_w-finger_w/2,0) 
        x, y = F2[0,2],F2[1,2]
        pygame.draw.circle(screen, RED, (x,y), radius=3) #joint position
        F21 = F2 @ Tmat(-finger_w/2,0)
        F22 = F21 @ Tmat(0,finger_h/2)@Rmat(-joint_angle_f1)@Tmat(0,-finger_h/2)
        draw(finger, F22, screen, BLACK)


        #finish
        pygame.display.flip()
        clock.tick(FPS)
    #end of while
#end of main()

if __name__ == "__main__":
    main()