import random
import time
import threading
import pyautogui
import keyboard
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Initialize colorama
init()

paused = False
manual_resume = False
override_pause = False  # For tracking if pause was manually overridden

# Configuration
active_duration = 20 * 60  # 20 minutes in seconds
pause_min = 40 * 60  # 40 minutes in seconds
pause_max = 3 * 60 * 60  # 3 hours in seconds

# Night schedule (random buffer between 11:00 - 11:13)
night_start = 23  # 11 PM
night_end = 11  # 11 AM
buffer_minutes = 13  # Allow random buffer up to 13 minutes

def toggle_pause():
    global paused
    paused = not paused
    if paused:
        print(f"{Fore.LIGHTRED_EX}PAUSED{Style.RESET_ALL} - Click END to resume")
    else:
        print(f"{Fore.LIGHTGREEN_EX}RUNNING{Style.RESET_ALL} - Click END to pause")

def generate_random_number_list(start, end):
    numbers = [i for i in range(start, end + 1) if i % 10 == 8]
    random.shuffle(numbers)
    return numbers

def get_random_interval():
    return random.uniform(0.7, 1.7)

def countdown_timer(seconds):
    for i in range(seconds, 0, -1):
        print(f"Activating in {i} seconds...", end='\r')
        time.sleep(1)
    print(" " * 30, end='\r')  # Clear the line

def type_with_delay(text):
    for char in text:
        while paused:  # Check if paused
            time.sleep(0.1)  # Sleep while paused
        pyautogui.typewrite(char)  # Type each character
        time.sleep(0.05)  # Delay between characters
    pyautogui.press('enter')  # Simulate pressing Enter

def is_night_time():
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute

    # Stop between 11 PM and 11 AM with a random buffer of up to 13 minutes
    if night_start <= current_hour or (current_hour == night_end and current_minute < random.randint(0, buffer_minutes)):
        return True
    elif current_hour < night_end or (current_hour == night_end and current_minute >= random.randint(0, buffer_minutes)):
        return False
    return False

def calculate_resume_time():
    pause_duration = random.uniform(pause_min, pause_max)
    return datetime.now() + timedelta(seconds=pause_duration)

def handle_scheduled_pause():
    global paused, manual_resume, override_pause
    while True:
        if not paused and not manual_resume and not override_pause:  # Only auto-pause if not manually resumed or overridden
            if is_night_time():
                random_start_minute = random.randint(0, buffer_minutes)
                print(f"Pausing due to night time. Will resume between 11:00 AM and 11:{random_start_minute} AM.")
                pause_until(datetime.now().replace(hour=night_end, minute=random_start_minute, second=0, microsecond=0))
            else:
                resume_time = calculate_resume_time()
                print(f"Pausing for {resume_time - datetime.now()} seconds. Will resume at {resume_time.strftime('%Y-%m-%d %H:%M:%S')}")
                pause_until(resume_time)
        time.sleep(1)  # Check every second

def pause_until(resume_time):
    global paused, override_pause
    paused = True
    while datetime.now() < resume_time and not manual_resume and not override_pause:
        time.sleep(1)
    if not override_pause:  # Only unpause automatically if not manually overridden
        paused = False
        print(f"{Fore.LIGHTGREEN_EX}Resumed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")

def override_manual_pause_with_custom_time():
    global paused, manual_resume, override_pause

    # Ask user for a custom stop time
    stop_time_str = input("Enter the custom time to pause (HH:MM): ")
    try:
        stop_time = datetime.strptime(stop_time_str, "%H:%M").time()
        now = datetime.now()

        # Combine today's date with the entered time to create the resume time
        resume_time = datetime.combine(now.date(), stop_time)

        # If the entered time is earlier in the day, schedule for the next day
        if resume_time < now:
            resume_time += timedelta(days=1)

        # Override and set custom pause time
        paused = False
        manual_resume = True
        override_pause = True
        print(f"{Fore.LIGHTGREEN_EX}Schedule Overridden - Will pause at {resume_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        pause_until(resume_time)

    except ValueError:
        print("Invalid time format. Please use HH:MM format.")

def main():
    global paused, manual_resume, override_pause

    # Set up hotkeys
    threading.Thread(target=lambda: keyboard.add_hotkey('end', toggle_pause)).start()  # Pause/resume with END key
    threading.Thread(target=lambda: keyboard.add_hotkey('del', override_manual_pause_with_custom_time)).start()  # Manual resume override with DEL key
    threading.Thread(target=handle_scheduled_pause, daemon=True).start()  # Schedule handling

    input("Type '.start' to begin counting: ")

    countdown_timer(20)

    count_limit = 500000
    random_numbers = generate_random_number_list(1, count_limit)

    for number in random_numbers:
        while paused:
            time.sleep(0.1)

        # Type the output with delay
        type_with_delay(str(number))

        print(f"{Fore.LIGHTGREEN_EX}Successfully Sent: {number}{Style.RESET_ALL}")
        time.sleep(get_random_interval())

if __name__ == "__main__":
    main()
