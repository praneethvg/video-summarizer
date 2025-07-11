"""
Summarization processor that handles TranscriptGeneratedEvent and emits SummaryCreatedEvent.
"""

import time
from pathlib import Path
from rich.console import Console

from src.events.handlers.event_handler import EventProcessor
from src.events import TranscriptGeneratedEvent, SummaryCreatedEvent, SummaryProcessingErrorEvent
from src.config import Config
from src.summarizer import AISummarizer
from src.utils import save_summary_to_file

console = Console()


class SummarizationProcessor(EventProcessor):
    """Processor that summarizes transcripts when TranscriptGeneratedEvent is received."""
    
    def __init__(self, event_bus, summary_style: str = "comprehensive", 
                 summary_length: str = "medium", output_format: str = "text"):
        super().__init__(event_bus, "SummarizationProcessor")
        self.summary_style = summary_style
        self.summary_length = summary_length
        self.output_format = output_format
        self.summarizer = AISummarizer(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
    
    def handle(self, event: TranscriptGeneratedEvent):
        """
        Handle TranscriptGeneratedEvent by generating a summary.
        
        Args:
            event: TranscriptGeneratedEvent containing transcript text
        """
        console.print(f"[blue]🤖 Generating {self.summary_style} summary ({self.summary_length})[/blue]")
        
        start_time = time.time()
        
        try:
            # Generate summary
            summary_result = self.summarizer.summarize(
                event.transcript_text,
                length=self.summary_length,
                style=self.summary_style
            )
            
            processing_duration = time.time() - start_time
            
            # Save summary to file
            output_path = self._save_summary(summary_result, event.video_id)
            
            # Emit SummaryCreatedEvent
            summary_event = SummaryCreatedEvent(
                video_id=event.video_id,
                summary_text=summary_result['summary'],
                format=self.output_format,
                summary_style=self.summary_style,
                summary_length=self.summary_length,
                word_count=summary_result['word_count'],
                model_used=summary_result['model_used'],
                tokens_used=summary_result.get('tokens_used'),
                processing_duration=processing_duration,
                output_path=output_path,
                source=self.name
            )
            
            self.publish_event(summary_event)
            return summary_result
            
        except Exception as e:
            # Emit error event
            error_event = SummaryProcessingErrorEvent(
                video_id=event.video_id,
                error_message=str(e),
                error_type=type(e).__name__,
                summary_style=self.summary_style,
                format=self.output_format,
                source=self.name
            )
            self.publish_event(error_event)
            raise
    
    def _save_summary(self, summary_result: dict, video_id: str) -> str:
        """Save summary to file and return the output path."""
        # Create output filename
        output_filename = f"{video_id}_{self.summary_style}_{self.summary_length}_{self.output_format}.{self.output_format}"
        output_path = Path(Config.OUTPUT_DIR) / output_filename
        
        if self.output_format == 'pdf':
            # For PDF, use structured style and convert to PDF
            if self.summary_style != 'structured':
                console.print("[yellow]⚠️  PDF format requires structured style. Switching to structured style.[/yellow]")
                self.summary_style = 'structured'
            
            # Generate structured summary
            structured_summary = self.summarizer.summarize(
                summary_result.get('original_text', ''),
                length=self.summary_length,
                style='structured'
            )
            
            # Convert to PDF
            if self.summarizer.markdown_to_pdf(structured_summary['summary'], str(output_path)):
                console.print(f"[green]✅ PDF summary saved to: {output_path}[/green]")
            else:
                console.print(f"[red]❌ Failed to generate PDF: {output_path}[/red]")
        else:
            # Use regular save method for other formats
            save_summary_to_file(summary_result, str(output_path), self.output_format)
            console.print(f"[green]✅ Summary saved to: {output_path}[/green]")
        
        return str(output_path)
    
    def handle_error(self, event: TranscriptGeneratedEvent, error: Exception):
        """Handle summarization errors by emitting error event."""
        error_event = SummaryProcessingErrorEvent(
            video_id=event.video_id,
            error_message=str(error),
            error_type=type(error).__name__,
            summary_style=self.summary_style,
            format=self.output_format,
            source=self.name
        )
        self.publish_event(error_event) 