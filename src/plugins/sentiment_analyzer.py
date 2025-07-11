"""
Sentiment analysis processor plugin for the YouTube summarizer.
"""

import time
from typing import List, Type, Dict, Any
from rich.console import Console

from src.plugins.base.plugin_base import ProcessorPlugin, PluginInfo
from src.events import TranscriptGeneratedEvent, SummaryCreatedEvent
from src.events.events.transcript_events import TranscriptSegment

console = Console()


class SentimentAnalyzer(ProcessorPlugin):
    """Sentiment analysis processor plugin."""
    
    def get_plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="sentiment_analyzer",
            version="1.0.0",
            description="Analyzes sentiment of video transcripts and summaries",
            author="YouTube Summarizer Team",
            plugin_type="processor",
            entry_point="SentimentAnalyzer",
            config_schema={
                "analysis_type": {"type": "string", "default": "basic", "choices": ["basic", "detailed"]},
                "confidence_threshold": {"type": "float", "default": 0.7}
            }
        )
    
    def get_event_types(self) -> List[Type]:
        return [TranscriptGeneratedEvent, SummaryCreatedEvent]
    
    def process_event(self, event) -> Dict[str, Any]:
        """Process events and analyze sentiment."""
        if isinstance(event, TranscriptGeneratedEvent):
            return self._analyze_transcript_sentiment(event)
        elif isinstance(event, SummaryCreatedEvent):
            return self._analyze_summary_sentiment(event)
        else:
            return {}
    
    def _analyze_transcript_sentiment(self, event: TranscriptGeneratedEvent) -> Dict[str, Any]:
        """Analyze sentiment of transcript."""
        console.print(f"[blue]😊 Analyzing transcript sentiment for video: {event.video_id}[/blue]")
        
        # Simple sentiment analysis (in a real implementation, you'd use a proper NLP library)
        text = event.transcript_text.lower()
        
        # Basic sentiment keywords
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'dislike', 'horrible', 'terrible']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Calculate sentiment score
        total_words = len(text.split())
        if total_words > 0:
            sentiment_score = (positive_count - negative_count) / total_words
        else:
            sentiment_score = 0.0
        
        # Determine sentiment
        if sentiment_score > 0.01:
            sentiment = "positive"
        elif sentiment_score < -0.01:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        analysis_result = {
            'video_id': event.video_id,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'total_words': total_words,
            'analysis_type': 'transcript',
            'processing_time': time.time()
        }
        
        console.print(f"[green]✅ Sentiment analysis complete: {sentiment} (score: {sentiment_score:.3f})[/green]")
        return analysis_result
    
    def _analyze_summary_sentiment(self, event: SummaryCreatedEvent) -> Dict[str, Any]:
        """Analyze sentiment of summary."""
        console.print(f"[blue]😊 Analyzing summary sentiment for video: {event.video_id}[/blue]")
        
        # Similar analysis for summary
        text = event.summary_text.lower()
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'dislike', 'horrible', 'terrible']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total_words = len(text.split())
        if total_words > 0:
            sentiment_score = (positive_count - negative_count) / total_words
        else:
            sentiment_score = 0.0
        
        if sentiment_score > 0.01:
            sentiment = "positive"
        elif sentiment_score < -0.01:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        analysis_result = {
            'video_id': event.video_id,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'total_words': total_words,
            'analysis_type': 'summary',
            'processing_time': time.time()
        }
        
        console.print(f"[green]✅ Summary sentiment analysis complete: {sentiment} (score: {sentiment_score:.3f})[/green]")
        return analysis_result
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get history of sentiment analyses."""
        # In a real implementation, you'd store this in a database
        return [] 