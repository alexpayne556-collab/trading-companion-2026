#!/usr/bin/env python3
"""
🐺 WOLF EYE - Individual Screen Watcher
Each eye watches one monitor/window and reports what it sees
"""

import threading
import queue
import time
from PIL import Image
import mss


class WolfEye:
    """
    A single eye watching a specific monitor or window.
    Reports what it sees to the brain.
    """
    
    def __init__(self, name, monitor_num=1, interval=3, analyze_func=None):
        """
        Args:
            name: Name of this eye (e.g., "Charts", "News", "Level2")
            monitor_num: Which monitor to watch (1, 2, 3...)
            interval: How often to capture (seconds)
            analyze_func: Custom function to analyze captured image
        """
        self.name = name
        self.monitor_num = monitor_num
        self.interval = interval
        self.analyze_func = analyze_func or self.default_analyze
        self.report_queue = queue.Queue()
        self.running = False
        self.last_capture = None
    
    def capture(self):
        """Capture this eye's target monitor"""
        try:
            with mss.mss() as sct:
                if self.monitor_num >= len(sct.monitors):
                    print(f"⚠️  {self.name}: Monitor {self.monitor_num} doesn't exist")
                    return None
                
                mon = sct.monitors[self.monitor_num]
                screenshot = sct.grab(mon)
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                self.last_capture = img
                return img
        except Exception as e:
            print(f"❌ {self.name} capture error: {e}")
            return None
    
    def default_analyze(self, image):
        """
        Default analyzer - just checks if image changed
        Override this with custom logic
        """
        if image is None:
            return []
        
        # For now, just report that we captured
        return [f"{self.name} watching (size: {image.size})"]
    
    def watch(self):
        """Main watch loop - runs in background thread"""
        self.running = True
        print(f"👁️  {self.name} watching Monitor {self.monitor_num}...")
        
        while self.running:
            try:
                # Capture
                img = self.capture()
                
                # Analyze
                if img:
                    alerts = self.analyze_func(img)
                    
                    # Report if anything important
                    if alerts:
                        self.report_queue.put({
                            'eye': self.name,
                            'time': time.time(),
                            'alerts': alerts,
                            'image': img  # Could attach image for brain to see
                        })
                
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"👁️  {self.name} error: {e}")
                time.sleep(1)
        
        print(f"👁️  {self.name} stopped")
    
    def start(self):
        """Start watching in background thread"""
        thread = threading.Thread(target=self.watch, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Stop watching"""
        self.running = False


# ============================================================================
# EXAMPLE ANALYZERS - Custom logic for different eye types
# ============================================================================

def chart_analyzer(image):
    """
    Analyzer for chart monitor
    TODO: Add OCR to read prices, volumes, indicators
    """
    alerts = []
    
    # For now, just check if screen changed significantly
    # In production, you'd:
    # - OCR read prices
    # - Detect volume bars
    # - Look for breakout patterns
    # - Read indicators
    
    return alerts


def news_analyzer(image):
    """
    Analyzer for news feed
    TODO: Add OCR to read headlines
    """
    alerts = []
    
    # In production:
    # - OCR read headlines
    # - Look for keywords: "8-K", "filing", "earnings", "contract"
    # - Look for your tickers
    # - Alert on important news
    
    return alerts


def level2_analyzer(image):
    """
    Analyzer for Level 2 / Order Flow
    TODO: Add OCR to read bid/ask
    """
    alerts = []
    
    # In production:
    # - Read bid/ask sizes
    # - Detect large orders
    # - Track when orders get lifted/hit
    # - Alert on unusual activity
    
    return alerts


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🐺 WOLF EYE TEST")
    print("="*70)
    
    # List available monitors
    with mss.mss() as sct:
        monitors = sct.monitors
        print(f"\nFound {len(monitors)-1} monitors:")
        for i, mon in enumerate(monitors):
            if i == 0:
                print(f"  Monitor {i}: ALL MONITORS (virtual)")
            else:
                print(f"  Monitor {i}: {mon['width']}x{mon['height']} "
                      f"at ({mon['left']}, {mon['top']})")
    
    # Create a test eye
    print("\nCreating test eye for Monitor 1...")
    eye = WolfEye("TestEye", monitor_num=1, interval=2)
    
    # Start watching
    print("Starting watch (will run for 10 seconds)...")
    eye.start()
    
    # Let it run
    time.sleep(10)
    
    # Check reports
    print("\nReports received:")
    while not eye.report_queue.empty():
        report = eye.report_queue.get()
        print(f"  {report['eye']}: {report['alerts']}")
    
    # Stop
    eye.stop()
    time.sleep(1)
    
    print("\n✅ Wolf Eye test complete")
