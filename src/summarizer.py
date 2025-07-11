"""
AI-powered text summarization module.
Uses OpenAI GPT models for intelligent summarization.
"""

import os
from typing import Dict, Any, Optional
from openai import OpenAI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from src.prompts.prompt_manager import PromptManager

console = Console()

class AISummarizer:
    """Handles AI-powered text summarization using OpenAI."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize AI summarizer.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (gpt-4, gpt-3.5-turbo)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.prompt_manager = PromptManager()
        
        console.print(f"[blue]Initialized AI Summarizer with model: {model}[/blue]")
    
    def summarize(self, text: str, length: str = "medium", style: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate AI summary of the given text.
        
        Args:
            text: Text to summarize
            length: Summary length (short, medium, long)
            style: Summary style (comprehensive, bullet_points, key_points, structured)
            
        Returns:
            Dictionary containing summary data
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Define length constraints
        length_constraints = {
            'short': 150,
            'medium': 300,
            'long': 500
        }
        
        max_length = length_constraints.get(length, 300)
        
        # Create prompt based on style using the prompt manager
        try:
            variables = {
                'text': text[:200000],  # Limit text length for large transcripts
                'max_length': max_length
            }
            prompt = self.prompt_manager.get_prompt(style, variables)
        except ValueError as e:
            # Fallback to default prompt if style not found
            console.print(f"[yellow]Warning: Unknown prompt style '{style}'. Using default.[/yellow]")
            default_style = self.prompt_manager.get_default_prompt()
            variables = {
                'text': text[:200000],
                'max_length': max_length
            }
            prompt = self.prompt_manager.get_prompt(default_style, variables)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating AI summary...", total=None)
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert content summarizer. Create clear, accurate, and engaging summaries."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4000,  # Increased significantly for detailed summaries
                    temperature=0.3,  # Balanced creativity and accuracy
                )
                
                summary = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
                
                progress.update(task, description="✅ Summary generated successfully!")
                
                return {
                    'summary': summary,
                    'length': length,
                    'style': style,
                    'word_count': len(summary.split()),
                    'model_used': self.model,
                    'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') and response.usage else None
                }
                
            except Exception as e:
                progress.update(task, description=f"❌ Summarization failed: {e}")
                raise
    

    
    def markdown_to_pdf(self, markdown_content: str, output_path: str) -> bool:
        """
        Convert markdown content to PDF with styling using reportlab.
        
        Args:
            markdown_content: Markdown text to convert
            output_path: Path for the output PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import markdown
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            import re
            
            # Convert markdown to HTML first
            html_content = markdown.markdown(markdown_content, extensions=['tables'])
            
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=8,
                textColor=colors.darkgreen
            )
            
            # Parse HTML and convert to reportlab elements
            lines = html_content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if line.startswith('<h1>'):
                    # Title
                    text = re.sub(r'<h1>(.*?)</h1>', r'\1', line)
                    story.append(Paragraph(text, title_style))
                    story.append(Spacer(1, 12))
                    
                elif line.startswith('<h2>'):
                    # Heading
                    text = re.sub(r'<h2>(.*?)</h2>', r'\1', line)
                    story.append(Paragraph(text, heading_style))
                    story.append(Spacer(1, 8))
                    
                elif line.startswith('<h3>'):
                    # Subheading
                    text = re.sub(r'<h3>(.*?)</h3>', r'\1', line)
                    story.append(Paragraph(text, styles['Heading3']))
                    story.append(Spacer(1, 6))
                    
                elif line.startswith('<table>'):
                    # Handle table
                    table_data = []
                    i += 1  # Skip <table> tag
                    while i < len(lines) and not lines[i].strip().startswith('</table>'):
                        if lines[i].strip().startswith('<tr>'):
                            row = []
                            i += 1
                            while i < len(lines) and not lines[i].strip().startswith('</tr>'):
                                cell_match = re.search(r'<t[dh]>(.*?)</t[dh]>', lines[i])
                                if cell_match:
                                    row.append(cell_match.group(1))
                                i += 1
                            if row:
                                table_data.append(row)
                        i += 1
                    
                    if table_data:
                        table = Table(table_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 12),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(table)
                        story.append(Spacer(1, 12))
                    
                elif line.startswith('<ul>') or line.startswith('<ol>'):
                    # Handle lists
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith('</ul>') and not lines[i].strip().startswith('</ol>'):
                        if lines[i].strip().startswith('<li>'):
                            text = re.sub(r'<li>(.*?)</li>', r'• \1', lines[i])
                            story.append(Paragraph(text, styles['Normal']))
                        i += 1
                    story.append(Spacer(1, 6))
                    
                elif line.startswith('<p>'):
                    # Paragraph
                    text = re.sub(r'<p>(.*?)</p>', r'\1', line)
                    # Convert markdown bold/italic
                    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
                    story.append(Paragraph(text, styles['Normal']))
                    story.append(Spacer(1, 6))
                    
                elif line and not line.startswith('<'):
                    # Plain text
                    text = line
                    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
                    story.append(Paragraph(text, styles['Normal']))
                    story.append(Spacer(1, 6))
                
                i += 1
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            console.print(f"[red]Error generating PDF: {e}[/red]")
            return False
    
    def get_available_prompts(self) -> Dict[str, str]:
        """Get list of available prompt styles with descriptions."""
        return self.prompt_manager.get_available_prompts()
    
    def get_prompt_info(self, prompt_key: str) -> Dict[str, Any]:
        """Get detailed information about a specific prompt."""
        return self.prompt_manager.get_variable_info(prompt_key)
    
    def estimate_cost(self, text_length: int, length: str = "medium") -> float:
        """
        Estimate the cost of summarization.
        
        Args:
            text_length: Length of input text
            length: Summary length
            
        Returns:
            Estimated cost in USD
        """
        # Rough cost estimates (as of 2024)
        if self.model == "gpt-4":
            input_cost_per_1k = 0.03
            output_cost_per_1k = 0.06
        else:  # gpt-3.5-turbo
            input_cost_per_1k = 0.0015
            output_cost_per_1k = 0.002
        
        input_tokens = text_length * 1.3  # Rough estimate
        output_tokens = {
            'short': 150,
            'medium': 300,
            'long': 500
        }.get(length, 300)
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
