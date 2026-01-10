#!/usr/bin/env python3
"""
🐺 WOLF PACK VISION SYSTEM
Multiple AI wolves watching your screen in real-time, hunting together

Each wolf sees what you see. Each has a specialty.
They talk to each other. They alert you when they agree.
"""

import time
import threading
import queue
from datetime import datetime
from collections import deque
import mss
from PIL import Image
import io
import base64
import json


class VisionProvider:
    """
    Interface to vision models (local or API)
    """
    
    def __init__(self, provider='ollama', model='llava'):
        self.provider = provider
        self.model = model
    
    def analyze_image(self, image, prompt):
        """
        Send image + prompt to vision model
        Returns text analysis
        """
        if self.provider == 'ollama':
            return self._analyze_ollama(image, prompt)
        elif self.provider == 'openai':
            return self._analyze_openai(image, prompt)
        elif self.provider == 'anthropic':
            return self._analyze_anthropic(image, prompt)
        else:
            return "Vision provider not configured"
    
    def _analyze_ollama(self, image, prompt):
        """Use local Ollama with LLaVA"""
        try:
            import requests
            
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Call Ollama API
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'images': [img_str],
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Ollama error: {e}"
    
    def _analyze_openai(self, image, prompt):
        """Use OpenAI GPT-4V"""
        # TODO: Implement OpenAI vision API
        return "OpenAI not implemented yet"
    
    def _analyze_anthropic(self, image, prompt):
        """Use Anthropic Claude with vision"""
        # TODO: Implement Anthropic vision API
        return "Anthropic not implemented yet"


class Wolf:
    """
    Base class for a wolf agent
    Each wolf sees the same screen but analyzes from their specialty
    """
    
    def __init__(self, name, specialty, vision_provider, alert_threshold=0.7):
        self.name = name
        self.specialty = specialty
        self.vision = vision_provider
        self.alert_threshold = alert_threshold
        self.observations = deque(maxlen=10)
        self.alerts = queue.Queue()
        self.running = False
    
    def get_analysis_prompt(self):
        """
        Each wolf has their own prompt based on specialty
        Override in subclasses
        """
        return f"Analyze this trading screen. Focus on: {self.specialty}"
    
    def analyze_screen(self, screenshot):
        """
        Wolf looks at screenshot and reports what it sees
        """
        prompt = self.get_analysis_prompt()
        analysis = self.vision.analyze_image(screenshot, prompt)
        
        observation = {
            'wolf': self.name,
            'time': datetime.now(),
            'analysis': analysis,
            'specialty': self.specialty
        }
        
        self.observations.append(observation)
        
        # Check if this is alert-worthy
        if self._is_important(analysis):
            self.alerts.put(observation)
        
        return observation
    
    def _is_important(self, analysis):
        """
        Determine if analysis warrants an alert
        Override in subclasses
        """
        # Keywords that indicate importance
        important_words = ['break', 'spike', 'unusual', 'alert', 'significant']
        return any(word in analysis.lower() for word in important_words)
    
    def speak(self, message):
        """Wolf communicates to pack"""
        return f"🐺 {self.name}: {message}"


class Fenrir(Wolf):
    """
    FENRIR - Chart Pattern Wolf
    Specialty: Technical analysis, patterns, support/resistance
    """
    
    def __init__(self, vision_provider):
        super().__init__(
            name="FENRIR",
            specialty="Chart patterns, breakouts, support/resistance",
            vision_provider=vision_provider
        )
    
    def get_analysis_prompt(self):
        return """You are FENRIR, a chart pattern expert wolf.

Look at this trading screen and tell me:
1. What tickers are visible?
2. Any breakouts or breakdown patterns?
3. Support/resistance levels being tested?
4. Volume patterns visible?
5. Any immediate trading opportunities?

Be concise. Focus on actionable patterns.
If you see something important, say "ALERT:" first."""


class Brokkr(Wolf):
    """
    BROKKR - News & Catalyst Wolf  
    Specialty: News, filings, catalysts, fundamental events
    """
    
    def __init__(self, vision_provider):
        super().__init__(
            name="BROKKR",
            specialty="News, catalysts, fundamental events",
            vision_provider=vision_provider
        )
    
    def get_analysis_prompt(self):
        return """You are BROKKR, a news and catalyst expert wolf.

Look at this trading screen and tell me:
1. Any news headlines visible?
2. Any SEC filings mentioned (8-K, Form 4, etc)?
3. Any earnings or revenue announcements?
4. Any catalyst events coming up?
5. What tickers have news?

Be concise. Focus on actionable catalysts.
If you see breaking news, say "ALERT:" first."""


class Heimdall(Wolf):
    """
    HEIMDALL - Volume & Order Flow Wolf
    Specialty: Volume, order flow, unusual activity
    """
    
    def __init__(self, vision_provider):
        super().__init__(
            name="HEIMDALL",
            specialty="Volume, order flow, unusual activity",
            vision_provider=vision_provider
        )
    
    def get_analysis_prompt(self):
        return """You are HEIMDALL, a volume and order flow expert wolf.

Look at this trading screen and tell me:
1. Any unusual volume spikes visible?
2. Any large orders on Level 2 (if visible)?
3. Volume compared to normal levels?
4. Any tickers showing abnormal activity?
5. Any signs of accumulation or distribution?

Be concise. Focus on unusual activity.
If you see significant volume, say "ALERT:" first."""


class Skoll(Wolf):
    """
    SKOLL - Sector & Correlation Wolf
    Specialty: Sector moves, correlation, rotation
    """
    
    def __init__(self, vision_provider):
        super().__init__(
            name="SKOLL",
            specialty="Sector trends, correlation, rotation",
            vision_provider=vision_provider
        )
    
    def get_analysis_prompt(self):
        return """You are SKOLL, a sector correlation expert wolf.

Look at this trading screen and tell me:
1. What sectors are represented?
2. Any sector-wide moves happening?
3. Which stocks moving together?
4. Any divergence (one stock weak while sector strong)?
5. Any rotation patterns visible?

Be concise. Focus on sector dynamics.
If you see sector rotation, say "ALERT:" first."""


class PackCoordinator:
    """
    The pack coordinator manages all wolves and facilitates communication
    """
    
    def __init__(self, wolves, capture_interval=10):
        self.wolves = wolves
        self.capture_interval = capture_interval
        self.pack_chat = deque(maxlen=100)
        self.running = False
        self.screen_queue = queue.Queue(maxsize=2)
    
    def capture_screens(self):
        """
        Continuously capture screens and put in queue
        """
        print("📸 Screen capture thread started")
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            
            while self.running:
                try:
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
                    
                    # Put in queue (non-blocking, drop if full)
                    try:
                        self.screen_queue.put_nowait(img)
                    except queue.Full:
                        pass
                    
                    time.sleep(self.capture_interval)
                    
                except Exception as e:
                    print(f"❌ Capture error: {e}")
                    time.sleep(1)
    
    def wolf_worker(self, wolf):
        """
        Worker thread for each wolf
        """
        print(f"🐺 {wolf.name} started hunting")
        
        while self.running:
            try:
                # Get latest screenshot (blocking)
                screenshot = self.screen_queue.get(timeout=1)
                
                # Wolf analyzes
                print(f"\n{'='*70}")
                print(f"🐺 {wolf.name} analyzing...")
                observation = wolf.analyze_screen(screenshot)
                
                # Share with pack
                self.pack_chat.append(observation)
                print(f"🐺 {wolf.name}: {observation['analysis'][:200]}...")
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ {wolf.name} error: {e}")
                time.sleep(1)
    
    def pack_discussion(self):
        """
        Wolves discuss what they're seeing
        Detect when multiple wolves alert on same ticker
        """
        print("💬 Pack discussion thread started")
        
        while self.running:
            time.sleep(5)  # Check every 5 seconds
            
            # Get recent observations (last 30 seconds)
            now = datetime.now()
            recent = [
                obs for obs in self.pack_chat 
                if (now - obs['time']).total_seconds() < 30
            ]
            
            if len(recent) >= 2:
                # Look for consensus
                tickers_mentioned = {}
                for obs in recent:
                    # Simple ticker extraction (you'd want better)
                    for ticker in ['APLD', 'WULF', 'CLSK', 'KTOS', 'CORZ', 
                                   'DNN', 'SMR', 'UEC', 'IONQ', 'RGTI']:
                        if ticker in obs['analysis']:
                            if ticker not in tickers_mentioned:
                                tickers_mentioned[ticker] = []
                            tickers_mentioned[ticker].append(obs['wolf'])
                
                # Alert if multiple wolves mention same ticker
                for ticker, wolves in tickers_mentioned.items():
                    if len(set(wolves)) >= 2:
                        self.pack_alert(ticker, wolves, recent)
    
    def pack_alert(self, ticker, wolves, observations):
        """
        Multiple wolves have spotted same ticker - ALERT TYR
        """
        print("\n" + "="*70)
        print(f"🚨🚨🚨 PACK ALERT: {ticker} 🚨🚨🚨")
        print("="*70)
        print(f"Wolves detecting: {', '.join(set(wolves))}")
        print("\nWhat they see:")
        
        for obs in observations:
            if ticker in obs['analysis']:
                print(f"\n🐺 {obs['wolf']}:")
                print(f"   {obs['analysis'][:300]}")
        
        print("\n" + "="*70)
        print("⚠️  MULTIPLE WOLVES AGREE - CHECK THIS NOW")
        print("="*70 + "\n")
        
        # TODO: Add sound, popup, more aggressive alert
    
    def hunt(self):
        """
        Start the pack hunt
        """
        self.running = True
        threads = []
        
        # Start screen capture
        capture_thread = threading.Thread(target=self.capture_screens, daemon=True)
        capture_thread.start()
        threads.append(capture_thread)
        
        # Start each wolf
        for wolf in self.wolves:
            wolf_thread = threading.Thread(target=self.wolf_worker, args=(wolf,), daemon=True)
            wolf_thread.start()
            threads.append(wolf_thread)
        
        # Start pack discussion
        discussion_thread = threading.Thread(target=self.pack_discussion, daemon=True)
        discussion_thread.start()
        threads.append(discussion_thread)
        
        print("\n" + "="*70)
        print("🐺 THE PACK IS HUNTING")
        print("="*70)
        print(f"Wolves active: {', '.join(w.name for w in self.wolves)}")
        print(f"Capture interval: {self.capture_interval}s")
        print("\nPress Ctrl+C to stop")
        print("="*70 + "\n")
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping pack hunt...")
            self.running = False
            time.sleep(2)
            print("✅ Pack hunt ended")
            print("🐺 LLHR. Until next hunt.")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("🐺 WOLF PACK VISION SYSTEM")
    print("="*70)
    
    # Setup vision provider
    print("\nInitializing vision provider...")
    vision = VisionProvider(provider='ollama', model='llava')
    
    # Create the pack
    print("Summoning the pack...")
    fenrir = Fenrir(vision)
    brokkr = Brokkr(vision)
    heimdall = Heimdall(vision)
    skoll = Skoll(vision)
    
    wolves = [fenrir, brokkr, heimdall, skoll]
    
    # Create coordinator
    coordinator = PackCoordinator(wolves, capture_interval=10)
    
    # Start hunting
    coordinator.hunt()


if __name__ == "__main__":
    main()
