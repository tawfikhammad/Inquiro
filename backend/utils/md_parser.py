import markdown
from config import DarkTheme

class MDParser:

    @staticmethod
    def markdown_to_html(markdown_text):
        html_content = markdown.markdown(markdown_text)

        # Define the mappings for markdown headings with custom styles
        markdown_to_html = {
            "#": f'<h1 style="color:{DarkTheme.HEADING_COLOR.value}">',
            "##": f'<h2 style="color:{DarkTheme.HEADING_COLOR.value}">',
            "###": f'<h3 style="color:{DarkTheme.HEADING_COLOR.value}">',
            "####": f'<h4 style="color:{DarkTheme.HEADING_COLOR.value}">',
            "#####": f'<h5 style="color:{DarkTheme.HEADING_COLOR.value}">',
            "######": f'<h6 style="color:{DarkTheme.HEADING_COLOR.value}">',
            "**": f'<b style="color:{DarkTheme.TEXT_COLOR.value}">',
            "*": f'<i style="color:{DarkTheme.TEXT_COLOR.value}">',
            "`": f'<code style="color:{DarkTheme.TEXT_COLOR.value}">',
            "```": f'<code style="color:{DarkTheme.TEXT_COLOR.value}">',
        }

        for markdown_tag, html_tag in markdown_to_html.items():
            opening_tag = html_tag
            closing_tag = html_tag.replace("<", "</")  # Create the closing tag
            html_content = html_content.replace(f"<{markdown_tag}>", opening_tag)
            html_content = html_content.replace(f"</{markdown_tag}>", closing_tag)

        return html_content