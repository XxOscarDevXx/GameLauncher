import pygame
import threading
import time

class ControllerManager:
    def __init__(self, input_callback):
        self.input_callback = input_callback
        self.running = True
        self.joysticks = []
        
        pygame.init()
        pygame.joystick.init()
        
        self.thread = threading.Thread(target=self._poll_inputs, daemon=True)
        self.thread.start()

    def _poll_inputs(self):
        while self.running:
            # Check for new controllers
            if pygame.joystick.get_count() != len(self.joysticks):
                self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
                for joy in self.joysticks:
                    joy.init()
            
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    # Button 0 is usually A/Cross (Select)
                    if event.button == 0:
                        self.input_callback("SELECT")
                    # Button 1 is usually B/Circle (Back)
                    elif event.button == 1:
                        self.input_callback("BACK")
                        
                elif event.type == pygame.JOYAXISMOTION:
                    # Vertical Axis (usually axis 1)
                    if event.axis == 1:
                        if event.value > 0.5:
                            self.input_callback("DOWN")
                            time.sleep(0.2) # Debounce
                        elif event.value < -0.5:
                            self.input_callback("UP")
                            time.sleep(0.2)
                            
                    # Horizontal Axis (usually axis 0)
                    elif event.axis == 0:
                        if event.value > 0.5:
                            self.input_callback("RIGHT")
                            time.sleep(0.2)
                        elif event.value < -0.5:
                            self.input_callback("LEFT")
                            time.sleep(0.2)
            
            time.sleep(0.01)

    def stop(self):
        self.running = False
