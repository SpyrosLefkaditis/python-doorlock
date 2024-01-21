import rp2
from rp2 import PIO
from machine import Pin
from time import sleep

@rp2.asm_pio(set_init=[PIO.IN_HIGH]*4)
def keypad():
    wrap_target()
    set(y, 0)                             # 0
    label("1")
    mov(isr, null)                        # 1
    set(pindirs, 1)                       # 2
    in_(pins, 4)                          # 3
    set(pindirs, 2)                       # 4
    in_(pins, 4)                          # 5
    set(pindirs, 4)                       # 6
    in_(pins, 4)                          # 7
    set(pindirs, 8)                       # 8
    in_(pins, 4)                          # 9
    mov(x, isr)                           # 10
    jmp(x_not_y, "13")                    # 11
    jmp("1")                              # 12
    label("13")
    push(block)                           # 13
    irq(0)
    mov(y, x)                             # 14
    jmp("1")                              # 15
    wrap()

for i in range(10, 14):
    Pin(i, Pin.IN, Pin.PULL_DOWN)

key_names = "*7410852#963DCBA"
input_code = "2005"  # Change this to your desired code
current_input = []

door_locked = True  # Initially, the door is locked

def oninput(machine):
    global door_locked

    keys = machine.get()
    while machine.rx_fifo():
        keys = machine.get()
    pressed = []
    for i in range(len(key_names)):
        if (keys & (1 << i)):
            pressed.append(key_names[i])

    current_input.extend(pressed)

    print("Keys changed! Pressed keys:", current_input)

    # Check if the pressed keys match the input code
    if len(current_input) >= len(input_code):
        if ''.join(current_input[-len(input_code):]) == input_code:
            if door_locked:
                print("Door Unlocked")
                door_locked = False
            else:
                print("Door is already unlocked")
            current_input.clear()
        elif "1" in pressed and not door_locked:
            print("Door Locked")
            door_locked = True
            current_input.clear()
        else:
            print("Incorrect Code")
            # Add a delay to allow time for the user to enter the complete code
            sleep(1)

sm = rp2.StateMachine(0, keypad, freq=2000, in_base=Pin(10, Pin.IN, Pin.PULL_DOWN), set_base=Pin(6))
sm.active(1)
sm.irq(oninput)

print("Please enter the code on the keypad, or press Ctrl+C to enter REPL.")
while True:
    sleep(0.1)
