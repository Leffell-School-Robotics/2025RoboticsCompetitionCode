# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       spenc                                                        #
# 	Created:      2/15/2025, 8:05:57 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

brain = Brain()
controller=Controller(PRIMARY)

####### DRIVE STUFF ↓ ########
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b)
right_motor_a = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
right_motor_b = Motor(Ports.PORT4, GearSetting.RATIO_18_1, True)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b)
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 319.19, 355.59999999999997, 266.7, MM, 1)

####### lift STUFF ↓ #######    

lift1 = Motor(Ports.PORT5, GearSetting.RATIO_36_1)
lift2 = Motor(Ports.PORT8, GearSetting.RATIO_36_1, True)
liftGroup = MotorGroup(lift1, lift2)

liftGroup.set_stopping(BrakeType.HOLD)

def on_up_button_pressed():
    if lift1.position() < -560:
        liftGroup.stop()
    else:
        liftGroup.spin(direction=REVERSE)

def on_down_button_pressed():
    if lift1.position() > 70:
        liftGroup.stop()
    else:
        liftGroup.spin(direction=FORWARD)
    
def on_lift_button_released():
    liftGroup.stop()

####### CLAW CODE ↓ ########

claw = Motor(Ports.PORT12)

claw.set_stopping(BrakeType.HOLD)
claw.set_velocity(17, PERCENT)

def on_close_button_pressed():
    claw.spin(direction=REVERSE)
    print(claw.position())

def on_open_button_pressed():
    claw.spin(direction=FORWARD)
    
def on_claw_button_released():
    claw.stop()
    
####### AUTONOMOUS CODE ↓ ########
def spinToClimbPosition():
    liftGroup.spin_to_position(-313, DEGREES, 100, PERCENT)
    drivetrain.drive_for(FORWARD, 400, MM, 100, PERCENT)
    liftGroup.spin_to_position(18, DEGREES, 100, PERCENT)
    
def rightAutonomous():
    drivetrain.drive_for(FORWARD, 100, MM, 60, PERCENT)
    liftGroup.spin_to_position(-540, DEGREES, 60, PERCENT)
    drivetrain.drive_for(FORWARD, 600, MM, 60, PERCENT)
    liftGroup.spin_to_position(-200, DEGREES, 100, PERCENT)
    claw.spin_for(REVERSE, 10, DEGREES, 60, PERCENT)
    drivetrain.turn_for(LEFT, 50, DEGREES, 60, PERCENT)
    drivetrain.drive_for(FORWARD, 100, MM, 60, PERCENT)
    liftGroup.spin_to_position(-300, DEGREES, 100, PERCENT)
    drivetrain.drive_for(FORWARD, 800, MM, 60, PERCENT)
    liftGroup.spin_to_position(18, DEGREES, 60, PERCENT)
    
def spinToSpikePosition():
    liftGroup.spin_to_position(-540, DEGREES, 60, PERCENT)
    
limit = Limit(brain.three_wire_port.a)
limit.pressed(lambda: liftGroup.reset_position())    

def autonomous():
    rightAutonomous()

def user_control():
    controller.buttonR1.pressed(on_up_button_pressed)
    controller.buttonR1.released(on_lift_button_released)
    controller.buttonL1.pressed(on_down_button_pressed)
    controller.buttonL1.released(on_lift_button_released)
    controller.buttonR2.pressed(on_open_button_pressed)
    controller.buttonR2.released(on_claw_button_released)
    controller.buttonL2.pressed(on_close_button_pressed)
    controller.buttonL2.released(on_claw_button_released)
    controller.buttonA.pressed(spinToClimbPosition)
    controller.buttonX.pressed(spinToSpikePosition)
    drivetrain_l_needs_to_be_stopped_controller = False
    drivetrain_r_needs_to_be_stopped_controller = False
    while True:
        if controller.axis3.position() > 0:
            drivetrain_left_side_speed = ((controller.axis3.position()**2) - 15)/150
        else:
            drivetrain_left_side_speed = -((controller.axis3.position()**2) - 15)/150
        if controller.axis2.position() > 0:
            drivetrain_right_side_speed = ((controller.axis2.position()**2) - 15)/150
        else:
            drivetrain_right_side_speed = -((controller.axis2.position()**2) - 15)/150
        
        # check if the value is inside of the deadband range
        if drivetrain_left_side_speed < 5 and drivetrain_left_side_speed > -5:
            # check if the left motor has already been stopped
            if drivetrain_l_needs_to_be_stopped_controller:
                # stop the left drive motor
                left_drive_smart.stop()
                # tell the code that the left motor has been stopped
                drivetrain_l_needs_to_be_stopped_controller = False
        else:
            # reset the toggle so that the deadband code knows to stop the left motor next
            # time the input is in the deadband range
            drivetrain_l_needs_to_be_stopped_controller = True
        # check if the value is inside of the deadband range
        if drivetrain_right_side_speed < 5 and drivetrain_right_side_speed > -5:
            # check if the right motor has already been stopped
            if drivetrain_r_needs_to_be_stopped_controller:
                # stop the right drive motor
                right_drive_smart.stop()
                # tell the code that the right motor has been stopped
                drivetrain_r_needs_to_be_stopped_controller = False
        else:
            # reset the toggle so that the deadband code knows to stop the right motor next
            # time the input is in the deadband range
            drivetrain_r_needs_to_be_stopped_controller = True
        
        # only tell the left drive motor to spin if the values are not in the deadband range
        if drivetrain_l_needs_to_be_stopped_controller:
            left_drive_smart.set_velocity(drivetrain_left_side_speed, PERCENT)
            left_drive_smart.spin(FORWARD)
        # only tell the right drive motor to spin if the values are not in the deadband range
        if drivetrain_r_needs_to_be_stopped_controller:
            right_drive_smart.set_velocity(drivetrain_right_side_speed, PERCENT)
            right_drive_smart.spin(FORWARD)
        # check the buttonL1/buttonL2 status
        # to control scooper_motor
        # wait before repeating the process
        wait(20, MSEC)

# create competition instance
comp = Competition(user_control, autonomous)

# actions to do when the program starts
brain.screen.clear_screen()