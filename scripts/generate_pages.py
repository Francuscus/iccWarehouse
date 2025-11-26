#!/usr/bin/env python3
"""
Page Generator - Build HTML pages from warehouse content using custom template
"""

import json
import os
import re
from pathlib import Path

class PageGenerator:
    def __init__(self, template_settings=None):
        """Initialize with template settings (colors, fonts, etc.)"""
        # Default settings (Ocean Blue preset)
        self.settings = {
            'PRIMARY_COLOR': '#667eea',
            'SECONDARY_COLOR': '#764ba2',
            'BG_COLOR': '#f5f7fa',
            'TEXT_COLOR': '#333333',
            'HEADING_FONT': 'Montserrat',
            'BODY_FONT': 'Open Sans',
            'CONTENT_WIDTH': '1400',
            'BORDER_RADIUS': '8'
        }
        
        # Override with custom settings if provided
        if template_settings:
            self.settings.update(template_settings)
        
        # Load template
        template_path = Path(__file__).parent.parent / 'templates' / 'page-template.html'
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()
    
    def apply_template_settings(self, html):
        """Replace template variables with actual values"""
        for key, value in self.settings.items():
            html = html.replace('{{' + key + '}}', str(value))
        return html
    
    def generate_page(self, page_data, subject_name, output_dir='output'):
        """Generate a single HTML page from warehouse data"""
        
        # Start with template
        html = self.template
        
        # Apply template settings (colors, fonts, etc.)
        html = self.apply_template_settings(html)
        
        # Replace page-specific content
        html = html.replace('{{TITLE}}', page_data['title'])
        html = html.replace('{{SUBJECT}}', subject_name)
        html = html.replace('{{CONTENT}}', page_data['full_content'])
        
        # Generate meta items
        meta_items = []
        if page_data.get('date'):
            meta_items.append(f'<div class="meta-item">📅 {page_data["date"]}</div>')
        
        if page_data.get('total_embeds', 0) > 0:
            embeds = page_data['embeds']
            if embeds['youtube'] > 0:
                meta_items.append(f'<div class="meta-item">🎥 {embeds["youtube"]} videos</div>')
            if embeds['google_forms'] > 0:
                meta_items.append(f'<div class="meta-item">📝 {embeds["google_forms"]} forms</div>')
            if embeds['google_slides'] > 0:
                meta_items.append(f'<div class="meta-item">📊 {embeds["google_slides"]} slides</div>')
        
        html = html.replace('{{META_ITEMS}}', '\n                '.join(meta_items))
        
        # Generate key terms section
        if page_data.get('key_terms'):
            terms_html = '<div class="key-terms">\n'
            terms_html += '    <h3>🔑 Key Concepts</h3>\n'
            terms_html += '    <div class="term-list">\n'
            for term in page_data['key_terms']:
                terms_html += f'        <span class="term-tag">{term}</span>\n'
            terms_html += '    </div>\n'
            terms_html += '</div>'
            html = html.replace('{{KEY_TERMS_SECTION}}', terms_html)
        else:
            html = html.replace('{{KEY_TERMS_SECTION}}', '')
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from slug
        filename = f"{page_data['slug']}.html"
        filepath = output_path / filename
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_from_subject(self, subject_file, output_dir='output'):
        """Generate all pages from a subject JSON file"""
        
        # Load subject data
        with open(subject_file, 'r', encoding='utf-8') as f:
            subject_data = json.load(f)
        
        subject_name = subject_data['subject']
        pages = subject_data['pages']
        
        print(f"\n📚 Generating {len(pages)} pages for: {subject_name}")
        print("=" * 70)
        
        generated_files = []
        
        for i, page in enumerate(pages, 1):
            try:
                filepath = self.generate_page(page, subject_name, output_dir)
                print(f"✅ {i}/{len(pages)}: {page['title'][:60]}")
                generated_files.append(filepath)
            except Exception as e:
                print(f"❌ Error generating {page['title']}: {e}")
        
        return generated_files
    
    def generate_all_subjects(self, data_dir='data', output_dir='output'):
        """Generate pages from all subject files"""
        
        data_path = Path(data_dir)
        subject_files = list(data_path.glob('subject_*.json'))
        
        print("\n" + "=" * 70)
        print("GENERATING ALL PAGES FROM WAREHOUSE")
        print("=" * 70)
        print(f"\nFound {len(subject_files)} subject files")
        print(f"Template settings: {self.settings}")
        
        all_generated = []
        
        for subject_file in subject_files:
            generated = self.generate_from_subject(subject_file, output_dir)
            all_generated.extend(generated)
        
        print("\n" + "=" * 70)
        print(f"✅ COMPLETE! Generated {len(all_generated)} pages")
        print(f"📁 Output directory: {output_dir}/")
        print("=" * 70)
        
        return all_generated

def load_custom_template():
    """Load custom template settings from localStorage (if running in browser)
    Or from template_settings.json if it exists"""
    
    settings_file = Path('template_settings.json')
    
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            print("✅ Loaded custom template settings")
            return settings
    
    return None

def main():
    """Main function - generate all pages with custom or default template"""
    
    print("\n🎨 PAGE GENERATOR")
    print("=" * 70)
    
    # Load custom template if available
    custom_settings = load_custom_template()
    
    if custom_settings:
        print("Using CUSTOM template settings from template_settings.json")
    else:
        print("Using DEFAULT template settings (Ocean Blue)")
        print("💡 Tip: Create template_settings.json to use custom colors/fonts")
    
    # Create generator
    generator = PageGenerator(custom_settings)
    
    # Generate all pages
    generated_files = generator.generate_all_subjects(
        data_dir='data',
        output_dir='output'
    )
    
    print("\n🎉 Your pages are ready!")
    print(f"📂 View them in the 'output/' folder")
    print(f"🌐 Upload to Hugging Face or GitHub Pages")

if __name__ == '__main__':
    main()
