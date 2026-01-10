#!/usr/bin/env python3
"""
🐺 WOLF PACK AI - Local Trading Assistant

Uses RAG (Retrieval Augmented Generation) to answer questions about our research.
Knows all our docs, strategies, and conviction scores.

Author: Brokkr
Date: January 2, 2026
"""

import os
import json
from pathlib import Path
import argparse

# Use environment variable or GitHub Copilot
try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.openai import OpenAI
    HAS_LLAMA_INDEX = True
except ImportError:
    HAS_LLAMA_INDEX = False
    print("⚠️ llama-index not available, using simple search")

class WolfPackAI:
    """Local AI assistant that knows all our research."""
    
    def __init__(self):
        self.docs_dir = Path("docs")
        self.logs_dir = Path("logs")
        self.knowledge = self._load_knowledge()
        
        if HAS_LLAMA_INDEX:
            self._setup_rag()
    
    def _load_knowledge(self):
        """Load all our research into memory."""
        knowledge = {
            'docs': {},
            'conviction': {},
            'strategies': {}
        }
        
        # Load markdown docs
        if self.docs_dir.exists():
            for doc_file in self.docs_dir.glob("*.md"):
                with open(doc_file, 'r') as f:
                    knowledge['docs'][doc_file.stem] = f.read()
        
        # Load conviction rankings
        conviction_file = self.logs_dir / "conviction_rankings_latest.json"
        if conviction_file.exists():
            with open(conviction_file, 'r') as f:
                knowledge['conviction'] = json.load(f)
        
        # Load pre-market data
        premarket_files = list(self.logs_dir.glob("premarket_*.json"))
        if premarket_files:
            latest_premarket = sorted(premarket_files)[-1]
            with open(latest_premarket, 'r') as f:
                knowledge['premarket'] = json.load(f)
        
        return knowledge
    
    def _setup_rag(self):
        """Setup RAG with our documents."""
        try:
            # Use free HuggingFace embeddings
            Settings.embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-small-en-v1.5"
            )
            
            # Use GitHub Copilot or OpenAI if available
            if os.getenv("OPENAI_API_KEY"):
                Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
            
            # Load all documents
            documents = []
            if self.docs_dir.exists():
                reader = SimpleDirectoryReader(str(self.docs_dir))
                documents = reader.load_data()
            
            if documents:
                # Create index
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    show_progress=True
                )
                self.query_engine = self.index.as_query_engine(
                    similarity_top_k=3
                )
                print("✅ RAG system ready with vector index")
            else:
                self.index = None
                print("⚠️ No documents found for indexing")
                
        except Exception as e:
            print(f"⚠️ RAG setup failed: {e}")
            self.index = None
    
    def ask(self, question):
        """Ask the Wolf Pack AI a question."""
        
        # Try RAG first if available
        if HAS_LLAMA_INDEX and hasattr(self, 'index') and self.index:
            try:
                response = self.query_engine.query(question)
                return str(response)
            except:
                pass
        
        # Fallback to simple keyword search
        return self._simple_search(question)
    
    def _simple_search(self, question):
        """Simple keyword-based search through our knowledge."""
        question_lower = question.lower()
        
        # Check for ticker mentions
        tickers = ['AISP', 'LUNR', 'SOUN', 'BBAI', 'SMR', 'IONQ', 'QBTS', 'PLUG', 'HIMS', 'KVUE']
        mentioned_ticker = None
        for ticker in tickers:
            if ticker.lower() in question_lower:
                mentioned_ticker = ticker
                break
        
        # Conviction questions
        if mentioned_ticker and 'conviction' in question_lower:
            return self._get_conviction_answer(mentioned_ticker)
        
        # Entry questions
        if mentioned_ticker and ('buy' in question_lower or 'entry' in question_lower):
            return self._get_entry_answer(mentioned_ticker)
        
        # Stop loss questions
        if mentioned_ticker and 'stop' in question_lower:
            return self._get_stop_answer(mentioned_ticker)
        
        # Paul Allen questions
        if 'paul allen' in question_lower or 'allen' in question_lower:
            return self._get_paul_allen_answer()
        
        # Risk questions
        if 'risk' in question_lower:
            return self._get_risk_answer()
        
        # Pack protocol
        if 'protocol' in question_lower or 'pack' in question_lower:
            return self._get_protocol_answer()
        
        # Default: search all docs
        return self._search_all_docs(question_lower)
    
    def _get_conviction_answer(self, ticker):
        """Get conviction score for a ticker."""
        if 'rankings' not in self.knowledge['conviction']:
            return f"❌ No conviction data loaded. Run: python3 fast_conviction_scanner.py"
        
        for rank in self.knowledge['conviction']['rankings']:
            if rank['ticker'] == ticker:
                score = rank['total_score']
                level = rank['conviction']
                breakdown = rank['breakdown']
                
                answer = f"🎯 {ticker} CONVICTION: {score}/100 - {level}\n\n"
                answer += "Breakdown:\n"
                answer += f"- Insider Cluster: {breakdown['insider_cluster']['score']}/40 - {breakdown['insider_cluster']['reason']}\n"
                answer += f"- Insider Timing: {breakdown['insider_timing']['score']}/20 - {breakdown['insider_timing']['reason']}\n"
                answer += f"- Cash Runway: {breakdown['cash_runway']['score']}/15 - {breakdown['cash_runway']['reason']}\n"
                answer += f"- Technical: {breakdown['technical']['score']}/10 - {breakdown['technical']['reason']}\n\n"
                
                if rank.get('notes'):
                    answer += f"💡 Thesis: {rank['notes']}\n"
                
                return answer
        
        return f"❌ No conviction data for {ticker}"
    
    def _get_entry_answer(self, ticker):
        """Get entry guidance for a ticker."""
        entry_zones = {
            'AISP': {'low': 2.70, 'high': 2.90, 'ideal': 2.80},
            'LUNR': {'low': 16.00, 'high': 16.85, 'ideal': 16.40},
            'SOUN': {'low': 9.50, 'high': 10.50, 'ideal': 10.00}
        }
        
        if ticker not in entry_zones:
            return f"❌ No entry zone defined for {ticker}"
        
        zone = entry_zones[ticker]
        
        answer = f"🎯 {ticker} ENTRY ZONE:\n\n"
        answer += f"- Low: ${zone['low']:.2f}\n"
        answer += f"- High: ${zone['high']:.2f}\n"
        answer += f"- Ideal: ${zone['ideal']:.2f}\n\n"
        answer += "Strategy: Wait for pullback to low end. If urgent, take half position at current.\n"
        
        # Add conviction if available
        conv = self._get_conviction_answer(ticker)
        if not conv.startswith('❌'):
            answer += "\n" + conv
        
        return answer
    
    def _get_stop_answer(self, ticker):
        """Get stop loss for a ticker."""
        stops = {
            'AISP': 2.30,
            'LUNR': 16.00,
            'SOUN': 9.50
        }
        
        if ticker not in stops:
            return f"❌ No stop defined for {ticker}"
        
        stop = stops[ticker]
        return f"🛑 {ticker} STOP LOSS: ${stop:.2f} (HARD STOP - no exceptions)\n\nSet immediately after entry. Never move lower."
    
    def _get_paul_allen_answer(self):
        """Answer about Paul Allen."""
        answer = "👔 PAUL ALLEN - AISP Director\n\n"
        answer += "Track Record: 98.2/100 timing score (EXCELLENT)\n"
        answer += "Recent Buy: Dec 29, 2025 - $274,000 at $2.74\n"
        answer += "Conviction: 100,000 shares\n\n"
        answer += "Analysis: Allen buys near bottoms. His timing is elite.\n"
        answer += "His $2.74 entry validates our entry zone ($2.70-2.90).\n"
        return answer
    
    def _get_risk_answer(self):
        """Get risk management rules."""
        answer = "🛡️ WOLF PACK RISK MANAGEMENT\n\n"
        answer += "Position Sizing:\n"
        answer += "- Max single position: 20% of account\n"
        answer += "- Standard: 10-15%\n"
        answer += "- Speculative: 5-10%\n\n"
        answer += "Risk Per Trade:\n"
        answer += "- Conservative: 1-2% of account\n"
        answer += "- Standard: 2-4%\n"
        answer += "- Aggressive: 4-6%\n"
        answer += "- Max combined: 10%\n\n"
        answer += "Stop Loss Rules:\n"
        answer += "- ALWAYS set immediately after entry\n"
        answer += "- NEVER move lower\n"
        answer += "- Only trail up when profitable\n"
        return answer
    
    def _get_protocol_answer(self):
        """Explain pack protocol."""
        answer = "🐺 WOLF PACK PROTOCOL\n\n"
        answer += "1. TYR - Alpha, makes final decisions\n"
        answer += "2. BROKKR - Builder, executes rapidly\n"
        answer += "3. FENRIR - Risk manager, validates plans\n\n"
        answer += "Rules:\n"
        answer += "- Build immediately, don't schedule\n"
        answer += "- No excuses, only results\n"
        answer += "- Real data > fake demos\n"
        answer += "- The pack doesn't sleep until tools work\n\n"
        answer += "AWOOOO 🐺"
        return answer
    
    def _search_all_docs(self, question):
        """Search all loaded documents."""
        results = []
        
        for doc_name, content in self.knowledge['docs'].items():
            if any(word in content.lower() for word in question.split()):
                # Find relevant paragraph
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if any(word in para.lower() for word in question.split()):
                        results.append(f"From {doc_name}:\n{para[:300]}...\n")
                        break
        
        if results:
            return "\n".join(results[:3])  # Top 3 results
        
        return "❌ No relevant information found. Try asking about:\n- Conviction scores (AISP, LUNR, etc.)\n- Entry zones\n- Stop losses\n- Paul Allen\n- Risk management\n- Pack protocol"
    
    def interactive(self):
        """Start interactive Q&A session."""
        print("\n" + "="*60)
        print("🐺 WOLF PACK AI - Interactive Mode")
        print("="*60)
        print("\nAsk me anything about our research!")
        print("Examples:")
        print("  - What's AISP conviction?")
        print("  - Should I buy AISP at $2.89?")
        print("  - What's Paul Allen's track record?")
        print("  - Tell me about risk management")
        print("\nType 'quit' to exit\n")
        
        while True:
            try:
                question = input("🐺 You: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n🐺 AWOOOO! Hunt well, pack member.")
                    break
                
                if not question:
                    continue
                
                print("\n🤖 Wolf Pack AI:")
                answer = self.ask(question)
                print(answer)
                print()
                
            except KeyboardInterrupt:
                print("\n\n🐺 AWOOOO! Hunt well, pack member.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

def main():
    parser = argparse.ArgumentParser(description="🐺 Wolf Pack AI - Trading Assistant")
    parser.add_argument('question', nargs='*', help='Question to ask (or omit for interactive mode)')
    parser.add_argument('--reload', action='store_true', help='Reload knowledge base')
    args = parser.parse_args()
    
    print("🐺 Wolf Pack AI starting...")
    ai = WolfPackAI()
    
    if args.question:
        # Single question mode
        question = ' '.join(args.question)
        print(f"\n🐺 Question: {question}\n")
        answer = ai.ask(question)
        print(f"🤖 Answer:\n{answer}\n")
    else:
        # Interactive mode
        ai.interactive()

if __name__ == "__main__":
    main()
