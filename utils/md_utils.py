# For RenderedView

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