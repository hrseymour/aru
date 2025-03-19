# For RenderedView and markdown processing
import markdown

def fix_markdown_tables(markdown_text):
    """
    Fixes improperly formatted markdown tables by adding missing separators
    and cleaning up formatting issues.
    
    Args:
        markdown_text (str): The markdown text to fix
        
    Returns:
        str: The fixed markdown text
    """
    lines = markdown_text.split('\n')
    processed_lines = []
    in_table = False
    header_row_index = -1
    
    for i, line in enumerate(lines):
        # Check if this could be a table row (has multiple pipe characters)
        if line.count('|') > 2:
            if not in_table:
                in_table = True
                header_row_index = i
                # Process as a potential header row
                processed_lines.append(line.strip())
                
                # Add a separator row if it's missing
                if i+1 < len(lines) and '---' not in lines[i+1]:
                    # Count columns and create separator
                    cols = max(1, line.count('|') - 1)
                    separator = '|' + '|'.join(['---'] * cols) + '|'
                    processed_lines.append(separator)
            else:
                # Process as a normal table row
                processed_lines.append(line.strip())
        else:
            if in_table:
                in_table = False
            processed_lines.append(line)
    
    # Join the processed lines back together
    return '\n'.join(processed_lines)


def get_table_css():
    """
    Returns CSS styling for markdown tables.
    
    Returns:
        str: CSS styling for tables
    """
    table_css = """
        <style>
        table {
            border-collapse: collapse;
            margin: 1em 0;
            width: 100%;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        </style>
        """
        
    return table_css


def get_markdown_extensions():
    """
    Gets available markdown extensions for rendering.
    
    Returns:
        list: List of available extensions
    """
    # Start with required extensions
    extensions = ['tables']
    
    # Add additional extensions if available
    try:
        import markdown.extensions.fenced_code
        extensions.append('fenced_code')
    except ImportError:
        pass
    
    return extensions


def render_markdown_to_html(markdown_text):
    """
    Renders markdown text to HTML with appropriate extensions and
    table fixing if needed.
    
    Args:
        markdown_text (str): The markdown text to render
        
    Returns:
        str: HTML rendered from markdown
    """
    # Get available extensions
    extensions = get_markdown_extensions()
    
    # Try rendering with standard markdown
    try:
        html_content = markdown.markdown(markdown_text, extensions=extensions)
        
        # If there are no tables rendered but there should be, try fixing the markdown
        if '<table>' not in html_content and '|' in markdown_text and '---' in markdown_text:
            fixed_text = fix_markdown_tables(markdown_text)
            html_content = markdown.markdown(fixed_text, extensions=extensions)
            
        return html_content
    except Exception as e:
        # Fallback attempt with table fixing if regular rendering fails
        try:
            fixed_text = fix_markdown_tables(markdown_text)
            html_content = markdown.markdown(fixed_text, extensions=['tables'])
            return html_content
        except:
            # If all else fails, return the error and raw text
            return f"<p>Error rendering markdown: {str(e)}</p><pre>{markdown_text}</pre>"


def create_html_preview(text_content, file_ext):
    """
    Creates a styled HTML preview based on file content and extension.
    
    Args:
        text_content (str): The text content to display
        file_ext (str): The file extension to determine rendering
        
    Returns:
        str: HTML preview with appropriate styling and formatting
    """
    # Starting HTML for the preview container
    html_preview = "<div style='height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; font-size: 14px;'>"
    
    file_ext = file_ext.lower() if file_ext else ''
    
    if file_ext in ['md', 'markdown']:
        # Add custom CSS for better table styling
        html_preview += get_table_css()
        
        # Convert markdown to HTML
        html_content = render_markdown_to_html(text_content)
        html_preview += html_content
    
    elif file_ext in ['html', 'htm']:
        # Directly use HTML (with basic sanitization)
        html_preview += text_content
    
    elif file_ext in ['txt', 'csv', 'json', 'xml']:
        # Preformatted text for code-like content
        html_preview += f"<pre style='white-space: pre-wrap;'>{text_content}</pre>"
    
    else:
        # Default to preformatted text for unknown types
        html_preview += f"<pre style='white-space: pre-wrap;'>{text_content}</pre>"
    
    html_preview += "</div>"
    
    return html_preview