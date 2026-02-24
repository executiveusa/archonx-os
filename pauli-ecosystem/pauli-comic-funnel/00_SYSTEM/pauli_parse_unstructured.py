#!/usr/bin/env python3
"""
PAULI Second Brain - LLM-Text Parsing Pipeline
Converts unstructured data (PDFs, Google Docs, ChatGPT exports) to machine-readable markdown

Usage:
    python pauli_parse_unstructured.py --input /path/to/exports --output ./01_PROJECTS
"""

import os
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PauliParser:
    """Main parser for converting unstructured data to structured markdown"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.metadata = {
            "parsed_date": datetime.now().isoformat(),
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "conversions": []
        }
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def install_llms_txt(self):
        """Ensure llms-txt is installed"""
        try:
            import llms_txt
            logger.info("✓ llms-txt already installed")
        except ImportError:
            logger.info("Installing llms-txt...")
            subprocess.run(["pip", "install", "llms-txt"], check=True)
            logger.info("✓ llms-txt installed")
    
    def parse_pdf(self, pdf_path: Path) -> str:
        """Parse PDF to markdown using llms-txt"""
        try:
            result = subprocess.run(
                ["llms-txt", str(pdf_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Failed to parse {pdf_path}: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Exception parsing {pdf_path}: {e}")
            return None
    
    def parse_google_docs_export(self, txt_path: Path) -> str:
        """Parse Google Docs text export to structured markdown"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert to markdown with structure
            return self._structure_text(content, txt_path.stem)
        except Exception as e:
            logger.error(f"Exception parsing {txt_path}: {e}")
            return None
    
    def parse_chatgpt_export(self, json_path: Path) -> str:
        """Parse ChatGPT conversation export"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            md_content = self._convert_chatgpt_to_markdown(data)
            return md_content
        except Exception as e:
            logger.error(f"Exception parsing ChatGPT export {json_path}: {e}")
            return None
    
    def _structure_text(self, content: str, title: str) -> str:
        """Add markdown structure to unstructured text"""
        lines = content.split('\n')
        
        # Create markdown with frontmatter
        md = f"""---
title: {title}
created: {datetime.now().isoformat()}
source: Google Docs Export
---

# {title}

"""
        md += '\n'.join(lines)
        return md
    
    def _convert_chatgpt_to_markdown(self, conv_data: Dict[str, Any]) -> str:
        """Convert ChatGPT JSON export to markdown"""
        md = f"""---
title: {conv_data.get('title', 'Untitled Conversation')}
created: {datetime.now().isoformat()}
source: ChatGPT Export
---

# {conv_data.get('title', 'Untitled Conversation')}

"""
        # Add conversation messages
        if 'mapping' in conv_data:
            for msg_id, msg_data in conv_data['mapping'].items():
                if msg_data.get('message'):
                    msg = msg_data['message']
                    author = msg.get('author', {}).get('name', 'Unknown')
                    content_parts = msg.get('content', {}).get('parts', [])
                    
                    md += f"\n## {author}\n\n"
                    for part in content_parts:
                        md += f"{part}\n\n"
        
        return md
    
    def process_all_files(self) -> Dict[str, Any]:
        """Process all files in input directory"""
        logger.info(f"Starting parse of {self.input_dir}...")
        
        supported_files = {
            '.pdf': self.parse_pdf,
            '.txt': self.parse_google_docs_export,
            '.json': self.parse_chatgpt_export,
            '.docx': self._parse_docx
        }
        
        for ext, parser_func in supported_files.items():
            files = list(self.input_dir.rglob(f"*{ext}"))
            logger.info(f"Found {len(files)} {ext} files")
            
            for file_path in files:
                self.metadata["total_files"] += 1
                logger.info(f"Processing {file_path.name}...")
                
                # Parse file
                parsed_content = parser_func(file_path)
                
                if parsed_content:
                    # Write output
                    output_path = self.output_dir / f"{file_path.stem}.md"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(parsed_content)
                    
                    self.metadata["successful"] += 1
                    self.metadata["conversions"].append({
                        "source": str(file_path),
                        "target": str(output_path),
                        "status": "success"
                    })
                    logger.info(f"✓ Saved to {output_path}")
                else:
                    self.metadata["failed"] += 1
                    logger.warning(f"✗ Failed to parse {file_path}")
        
        # Create manifest
        self._create_manifest()
        
        return self.metadata
    
    def _parse_docx(self, docx_path: Path) -> str:
        """Parse DOCX files"""
        try:
            result = subprocess.run(
                ["python", "-m", "docx2txt", str(docx_path)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return self._structure_text(result.stdout, docx_path.stem)
        except Exception as e:
            logger.error(f"Exception parsing {docx_path}: {e}")
        return None
    
    def _create_manifest(self):
        """Create manifest file for parsed content"""
        manifest_path = self.output_dir / "PARSE_MANIFEST.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        logger.info(f"Manifest saved to {manifest_path}")
        logger.info(f"\nParsing Summary:")
        logger.info(f"  Total files: {self.metadata['total_files']}")
        logger.info(f"  Successful: {self.metadata['successful']}")
        logger.info(f"  Failed: {self.metadata['failed']}")


def main():
    parser = argparse.ArgumentParser(
        description="Parse unstructured data into machine-readable markdown"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input directory with unstructured files"
    )
    parser.add_argument(
        "--output",
        default="./01_PROJECTS",
        help="Output directory for parsed markdown"
    )
    
    args = parser.parse_args()
    
    pauli = PauliParser(args.input, args.output)
    pauli.install_llms_txt()
    results = pauli.process_all_files()
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
