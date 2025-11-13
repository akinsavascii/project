import os
import subprocess
import tempfile

def text_to_pdf(text, out_path):
    """Convert text to PDF using wkhtmltopdf or libreoffice for proper Unicode support."""
    
    # Method 1: Try wkhtmltopdf (fast, good for text)
    try:
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20mm;
            line-height: 1.6;
            font-size: 11pt;
            color: #333;
        }}
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <pre>{text}</pre>
</body>
</html>
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            html_path = f.name
        
        try:
            # Try wkhtmltopdf
            result = subprocess.run(
                ['which', 'wkhtmltopdf'],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                subprocess.run(
                    ['wkhtmltopdf', '--quiet', html_path, out_path],
                    timeout=30,
                    check=False
                )
                if os.path.exists(out_path):
                    return
        except:
            pass
        
        # Try libreoffice (macOS often has it)
        try:
            subprocess.run(
                ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(out_path), html_path],
                timeout=30,
                check=False
            )
            temp_pdf = html_path.replace('.html', '.pdf')
            if os.path.exists(temp_pdf):
                os.rename(temp_pdf, out_path)
                return
        except:
            pass
        
    except Exception as e:
        print(f"HTML->PDF methods failed: {e}")
    finally:
        if os.path.exists(html_path):
            os.unlink(html_path)
    
    # Fallback: Save as plaintext with .pdf extension
    # This is readable as text but not a true PDF
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
