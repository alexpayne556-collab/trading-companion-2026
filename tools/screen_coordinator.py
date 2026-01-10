#!/usr/bin/env python3
"""
🐺 WOLF SCREEN COORDINATOR - Multi-Eye Brain
Receives reports from all eyes, connects dots, alerts on patterns
"""

import time
from collections import defaultdict, deque
from datetime import datetime


class ScreenCoordinator:
    """
    The coordinator listens to multiple wolf eyes watching different screens.
    It connects dots across screens and alerts when multiple signals align.
    """
    
    def __init__(self, eyes, alert_window=60):
        """
        Args:
            eyes: List of WolfEye instances
            alert_window: Time window (seconds) to correlate alerts
        """
        self.eyes = eyes
        self.alert_window = alert_window
        self.recent_alerts = defaultdict(lambda: deque(maxlen=50))
        self.ticker_signals = defaultdict(list)
        self.running = False
        
        # Tickers to watch
        self.watchlist = [
            'APLD', 'WULF', 'CORZ', 'CLSK', 'KTOS', 'BTBT', 'CIFR', 'IREN',
            'SMR', 'DNN', 'UEC', 'UUUU', 'CCJ', 'URG', 'NXE', 'BWXT',
            'LUNR', 'RKLB', 'ACHR', 'NVVE', 'IONQ', 'RGTI', 'QBTS'
        ]
    
    def listen(self):
        """
        Main loop - listen to all eyes and process reports
        """
        self.running = True
        print("🧠 Screen Coordinator listening to eyes...")
        
        try:
            while self.running:
                # Check each eye for new reports
                for eye in self.eyes:
                    while not eye.report_queue.empty():
                        report = eye.report_queue.get()
                        self.process_report(report)
                
                # Look for patterns across eyes
                self.connect_dots()
                
                # Check for ticker-specific multi-signals
                self.check_ticker_signals()
                
                time.sleep(0.5)  # Check twice per second
                
        except KeyboardInterrupt:
            print("\n🧠 Coordinator shutting down...")
        finally:
            self.running = False
    
    def process_report(self, report):
        """
        Process a report from an eye
        """
        eye_name = report['eye']
        alerts = report['alerts']
        timestamp = report['time']
        
        # Log each alert
        for alert in alerts:
            print(f"👁️  {eye_name}: {alert}")
            
            # Store alert
            self.recent_alerts[eye_name].append({
                'alert': alert,
                'time': timestamp
            })
            
            # Extract tickers from alert
            for ticker in self.watchlist:
                if ticker in alert:
                    self.ticker_signals[ticker].append({
                        'eye': eye_name,
                        'alert': alert,
                        'time': timestamp
                    })
    
    def connect_dots(self):
        """
        Look for patterns across different eyes
        """
        now = time.time()
        
        # Example: If multiple eyes report in short time, that's suspicious
        recent_eye_count = 0
        for eye_name, alerts in self.recent_alerts.items():
            if alerts and (now - alerts[-1]['time']) < 5:  # Last 5 seconds
                recent_eye_count += 1
        
        if recent_eye_count >= 3:
            # Multiple eyes active - something happening
            pass  # Could alert here
    
    def check_ticker_signals(self):
        """
        Check if multiple signals firing for same ticker
        """
        now = time.time()
        
        for ticker, signals in list(self.ticker_signals.items()):
            # Only recent signals
            recent = [s for s in signals if now - s['time'] < self.alert_window]
            
            if len(recent) >= 2:
                # Multiple signals on same ticker
                eyes_involved = set(s['eye'] for s in recent)
                
                if len(eyes_involved) >= 2:
                    # MULTI-EYE ALERT
                    self.alert_multi_signal(ticker, recent, eyes_involved)
                    
                    # Clear after alerting
                    self.ticker_signals[ticker] = []
    
    def alert_multi_signal(self, ticker, signals, eyes):
        """
        Alert user when multiple eyes see same ticker
        """
        message = f"""
{'='*70}
🚨 MULTI-SIGNAL ALERT: {ticker} 🚨
{'='*70}
Eyes detecting: {', '.join(eyes)}

Signals:
"""
        for signal in signals:
            message += f"  • {signal['eye']}: {signal['alert']}\n"
        
        message += f"\n⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        message += f"\n{'='*70}"
        
        print(message)
        
        # TODO: Add sound, popup, voice alert
        self.beep_alert()
    
    def alert_user(self, message, priority='normal'):
        """
        Alert the user with message
        """
        print(f"\n{'='*70}")
        print(message)
        print(f"{'='*70}\n")
        
        if priority == 'high':
            self.beep_alert()
    
    def beep_alert(self):
        """
        Make a sound (Linux compatible)
        """
        try:
            import os
            os.system('play -nq -t alsa synth 0.3 sine 1000 2>/dev/null')
        except:
            # Fallback: print bell character
            print('\a')
    
    def stop(self):
        """Stop the coordinator"""
        self.running = False


# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    from wolf_eye import WolfEye
    
    print("="*70)
    print("🐺 SCREEN COORDINATOR TEST")
    print("="*70)
    
    # Create mock eyes
    eye1 = WolfEye("Charts", monitor_num=1, interval=2)
    eye2 = WolfEye("News", monitor_num=1, interval=3)
    
    # Create coordinator
    coordinator = ScreenCoordinator([eye1, eye2])
    
    # Start eyes
    print("\nStarting eyes...")
    eye1.start()
    eye2.start()
    
    # Inject test reports
    print("\nInjecting test signals...")
    
    # Simulate APLD appearing on multiple screens
    eye1.report_queue.put({
        'eye': 'Charts',
        'time': time.time(),
        'alerts': ['APLD volume spike detected']
    })
    
    time.sleep(0.5)
    
    eye2.report_queue.put({
        'eye': 'News',
        'time': time.time(),
        'alerts': ['APLD 8-K filing detected']
    })
    
    # Run coordinator for 5 seconds
    print("\nCoordinator processing (5 seconds)...")
    import threading
    coordinator_thread = threading.Thread(target=coordinator.listen, daemon=True)
    coordinator_thread.start()
    
    time.sleep(5)
    
    # Stop everything
    print("\nStopping...")
    coordinator.stop()
    eye1.stop()
    eye2.stop()
    time.sleep(1)
    
    print("\n✅ Screen Coordinator test complete")
