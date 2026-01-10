#!/usr/bin/env python3
"""
🐺 WOLF PACK SCREEN READER
Multi-monitor real-time screen analysis system

Watches multiple screens simultaneously and alerts when patterns emerge.
"""

import sys
import time
import mss
from wolf_eye import WolfEye
from screen_coordinator import ScreenCoordinator


def list_monitors():
    """List all available monitors"""
    with mss.mss() as sct:
        monitors = sct.monitors
        print("="*70)
        print("🐺 AVAILABLE MONITORS")
        print("="*70)
        
        for i, mon in enumerate(monitors):
            if i == 0:
                print(f"Monitor {i}: ALL MONITORS (virtual)")
                print(f"           {mon['width']}x{mon['height']}")
            else:
                print(f"Monitor {i}: {mon['width']}x{mon['height']} "
                      f"at position ({mon['left']}, {mon['top']})")
        
        print("="*70)
        return len(monitors) - 1


def main():
    """
    Main entry point
    """
    print("="*70)
    print("🐺 WOLF PACK SCREEN READER")
    print("="*70)
    
    # List monitors
    num_monitors = list_monitors()
    
    if num_monitors == 0:
        print("❌ No monitors detected!")
        return
    
    print(f"\nDetected {num_monitors} monitor(s)")
    
    # Create eyes for each monitor
    eyes = []
    
    # Monitor 1 - Primary (usually your main trading screen)
    print("\nCreating Eye 1 for Monitor 1...")
    eye1 = WolfEye(
        name="Primary", 
        monitor_num=1, 
        interval=3
    )
    eyes.append(eye1)
    
    # If multiple monitors, create more eyes
    if num_monitors >= 2:
        print("Creating Eye 2 for Monitor 2...")
        eye2 = WolfEye(
            name="Secondary",
            monitor_num=2,
            interval=3
        )
        eyes.append(eye2)
    
    if num_monitors >= 3:
        print("Creating Eye 3 for Monitor 3...")
        eye3 = WolfEye(
            name="Tertiary",
            monitor_num=3,
            interval=3
        )
        eyes.append(eye3)
    
    # Create coordinator
    print("\nCreating Screen Coordinator...")
    coordinator = ScreenCoordinator(eyes, alert_window=60)
    
    # Start all eyes
    print("\n" + "="*70)
    print("🚀 STARTING WOLF PACK")
    print("="*70)
    
    for eye in eyes:
        eye.start()
        print(f"✅ {eye.name} eye watching Monitor {eye.monitor_num}")
    
    # Start coordinator
    print("✅ Coordinator active")
    print("\n" + "="*70)
    print("🐺 WOLF PACK ONLINE - Watching your screens...")
    print("Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    try:
        # Run coordinator in main thread
        coordinator.listen()
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 SHUTTING DOWN WOLF PACK")
        print("="*70)
    finally:
        # Stop everything
        coordinator.stop()
        for eye in eyes:
            eye.stop()
        time.sleep(1)
        print("✅ All eyes closed")
        print("🐺 LLHR. Until next hunt.")


if __name__ == "__main__":
    main()
