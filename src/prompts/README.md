# Prompt System Documentation

This directory contains the configurable prompt system for the AI summarizer. Prompts are stored as separate text files and can use variable substitution.

## Directory Structure

```
src/prompts/
├── README.md              # This documentation file
├── config.yaml            # Prompt configuration (maps keys to files)
├── prompt_manager.py      # Prompt management system
├── comprehensive.txt      # Comprehensive summary prompt
├── bullet_points.txt      # Bullet-point style prompt
├── key_points.txt         # Key points extraction prompt
├── structured.txt         # Structured markdown prompt
└── technical.txt          # Technical summary prompt
```

## How It Works

1. **Prompt Files**: Each prompt is stored as a `.txt` file with variable placeholders
2. **Configuration**: `config.yaml` maps prompt keys to file paths
3. **Variable Substitution**: Variables are substituted using Python's `.format()` method
4. **Usage**: The `PromptManager` class loads prompts and handles variable substitution

## Available Prompts

### comprehensive
- **File**: `comprehensive.txt`
- **Description**: Comprehensive summary with detailed analysis
- **Variables**: `text`, `max_length`
- **Use Case**: General-purpose summaries with full context

### bullet_points
- **File**: `bullet_points.txt`
- **Description**: Bullet-point style summary
- **Variables**: `text`, `max_length`
- **Use Case**: Quick, scannable summaries

### key_points
- **File**: `key_points.txt`
- **Description**: Key points extraction
- **Variables**: `text`, `max_length`
- **Use Case**: Focused on main insights and takeaways

### structured
- **File**: `structured.txt`
- **Description**: Structured markdown summary for investment analysis
- **Variables**: `text`
- **Use Case**: Investment news and financial content

### technical
- **File**: `technical.txt`
- **Description**: Technical summary focusing on technical details and methodologies
- **Variables**: `text`, `max_length`
- **Use Case**: Technical content, tutorials, documentation

## Variables

### Common Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `text` | string | The content to summarize | Full transcript or text content |
| `max_length` | integer | Target word count for summary | 300, 500, 1000 |

### Variable Usage

Variables are used in prompt files with curly braces:

```
Please summarize the following text in about {max_length} words:

{text}

Summary:
```

## Adding New Prompts

### 1. Create the Prompt File

Create a new `.txt` file in the `src/prompts/` directory:

```txt
# src/prompts/my_custom_prompt.txt
Please create a {style} summary of the following content:

{text}

The summary should be approximately {max_length} words and focus on {focus_area}.

Summary:
```

### 2. Update Configuration

Add the new prompt to `config.yaml`:

```yaml
prompts:
  # ... existing prompts ...
  my_custom_prompt:
    path: "src/prompts/my_custom_prompt.txt"
    description: "Custom prompt for specific use case"
    variables:
      - text
      - max_length
      - style
      - focus_area
```

### 3. Use the New Prompt

```python
from src.prompts.prompt_manager import PromptManager

manager = PromptManager()
variables = {
    'text': 'Your content here...',
    'max_length': 300,
    'style': 'detailed',
    'focus_area': 'technical concepts'
}
prompt = manager.get_prompt('my_custom_prompt', variables)
```

## Best Practices

### 1. Variable Naming
- Use descriptive, lowercase variable names
- Use underscores for multi-word variables (`max_length`, not `maxLength`)
- Keep variable names consistent across prompts

### 2. Prompt Design
- Be specific about the desired output format
- Include clear instructions for the AI
- Use consistent formatting across similar prompts
- Test prompts with various input types

### 3. Documentation
- Update this README when adding new prompts
- Document any special variable requirements
- Include usage examples for complex prompts

## CLI Commands

### List Available Prompts
```bash
python main.py --list-prompts
```

This command shows:
- All available prompt styles
- Descriptions for each prompt
- Variables used by each prompt

## Troubleshooting

### Common Issues

1. **Missing Variable Error**
   ```
   ValueError: Missing required variable in prompt 'comprehensive': 'text'
   ```
   **Solution**: Ensure all required variables are provided when calling `get_prompt()`

2. **Unknown Prompt Key Error**
   ```
   ValueError: Unknown prompt key: 'nonexistent_prompt'
   ```
   **Solution**: Check that the prompt key exists in `config.yaml`

3. **File Not Found Error**
   ```
   FileNotFoundError: Prompt file not found: src/prompts/missing.txt
   ```
   **Solution**: Ensure the prompt file exists at the path specified in `config.yaml`

### Debugging

To debug prompt issues:

1. Check the prompt file exists and is readable
2. Verify the path in `config.yaml` is correct
3. Ensure all required variables are provided
4. Test variable substitution manually

```python
# Debug example
manager = PromptManager()
print(manager.get_available_prompts())  # List all prompts
print(manager.get_variable_info('comprehensive'))  # Check variables
``` 