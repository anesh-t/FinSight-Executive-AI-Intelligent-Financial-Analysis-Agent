"""
Main Pipeline - Orchestrates HTML to JSON conversion
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from .config import HTMLParserConfig
    from .pdf_parser import PDFParser
    from .table_extractor import TableExtractor
    from .text_rewriter import TextRewriter
    from .text_chunker import TextChunker
except ImportError:
    from config import HTMLParserConfig
    from pdf_parser import PDFParser
    from table_extractor import TableExtractor
    from text_rewriter import TextRewriter
    from text_chunker import TextChunker

class HTMLToJSONPipeline:
    """Main pipeline for converting 10-K HTML to structured JSON"""
    
    def __init__(self, config: Optional[HTMLParserConfig] = None):
        self.config = config or HTMLParserConfig()
        self.config.ensure_directories()
        self.pdf_parser = PDFParser(self.config)
        self.table_extractor = TableExtractor(self.config)
        self.text_rewriter = TextRewriter(self.config)
        self.text_chunker = TextChunker(self.config)
        
    def process_file(self, pdf_file: Path) -> dict:
        """Process a single PDF file"""
        
        print(f"\n{'='*80}")
        print(f"🚀 Processing: {pdf_file.name}")
        print(f"{'='*80}\n")
        
        start_time = datetime.now()
        
        try:
            # Parse PDF
            parsed_data = self.pdf_parser.parse_pdf_file(str(pdf_file))
            
            metadata = parsed_data['metadata']
            sections = parsed_data['sections']
            
            print(f"\n📝 Processing {len(sections)} sections...")
            
            structured_json = {
                "document_metadata": {
                    **metadata,
                    "processing_date": datetime.now().isoformat(),
                    "pipeline_version": "1.0.0"
                },
                "items": {}
            }
            
            total_chunks = 0
            total_tables = 0
            total_rewrites = 0
            
            for section in sections:
                item_key = section['item']
                heading = section['heading']
                text = section['text']
                tables = section.get('tables', [])
                
                if item_key not in structured_json["items"]:
                    structured_json["items"][item_key] = {
                        "heading": heading,
                        "content": []
                    }
                
                rewritten_text = self.text_rewriter.rewrite_if_needed(text, heading)
                if rewritten_text != text:
                    total_rewrites += 1
                
                chunks = self.text_chunker.chunk_if_needed(rewritten_text, heading)
                total_chunks += len(chunks)
                
                for chunk in chunks:
                    # Always generate subheading if missing
                    subheading = chunk.get('subheading')
                    if not subheading:
                        print(f"   🤖 Generating subheading for {item_key}...")
                        subheading = self.text_rewriter.generate_subheading(chunk['text'][:500], heading)
                    
                    content_item = {
                        "subheading": subheading,
                        "text": chunk['text'],
                        "word_count": chunk['word_count']
                    }
                    
                    if chunk.get('subheading') or subheading:
                        content_item["subheading_generated"] = True
                    
                    if chunk.get('chunk_index'):
                        content_item["chunk_info"] = {
                            "index": chunk['chunk_index'],
                            "total": chunk['total_chunks']
                        }
                    
                    structured_json["items"][item_key]["content"].append(content_item)
                
                if self.config.ENABLE_TABLE_FORMATTING and tables:
                    formatted_tables = self.table_extractor.process_tables(tables)
                    total_tables += len(formatted_tables)
                    
                    for table in formatted_tables:
                        structured_json["items"][item_key]["content"].append({
                            "type": "table",
                            "subheading": "Financial Data Table",
                            "table_data": {
                                "header": table.get('header', []),
                                "rows": table.get('rows', []),
                            },
                            "num_rows": table.get('num_rows', 0),
                            "num_cols": table.get('num_cols', 0)
                        })
            
            self._save_output(structured_json, pdf_file.name)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"\n{'='*80}")
            print(f"✅ Processing Complete!")
            print(f"   Sections: {len(sections)}")
            print(f"   Text chunks: {total_chunks}")
            print(f"   Tables: {total_tables}")
            print(f"   Text rewrites: {total_rewrites}")
            print(f"   Time: {processing_time:.2f}s")
            print(f"{'='*80}\n")
            
            return {
                "success": True,
                "output_file": str(self.config.OUTPUT_DIR / f"{pdf_file.stem}_structured.json"),
                "stats": {
                    "sections": len(sections),
                    "chunks": total_chunks,
                    "tables": total_tables,
                    "rewrites": total_rewrites
                }
            }
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _save_output(self, data: dict, filename: str):
        """Save structured JSON"""
        
        output_filename = filename.replace('.pdf', '').replace('.PDF', '') + '_structured.json'
        output_path = self.config.OUTPUT_DIR / output_filename
        
        print(f"\n💾 Saving to: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved!")
    
    def process_all_files(self):
        """Process all PDF files in input directory"""
        
        pdf_files = list(self.config.INPUT_DIR.glob("*.pdf")) + \
                   list(self.config.INPUT_DIR.glob("*.PDF"))
        
        if not pdf_files:
            print(f"❌ No PDF files found in {self.config.INPUT_DIR}")
            return
        
        print(f"\n{'='*80}")
        print(f"🔄 Found {len(pdf_files)} PDF file(s)")
        print(f"{'='*80}")
        
        results = []
        for pdf_file in pdf_files:
            result = self.process_file(pdf_file)
            results.append(result)
        
        successful = sum(1 for r in results if r.get('success'))
        
        print(f"\n{'='*80}")
        print(f"📊 BATCH SUMMARY")
        print(f"{'='*80}")
        print(f"   Total: {len(results)}")
        print(f"   ✅ Success: {successful}")
        print(f"   ❌ Failed: {len(results) - successful}")
        print(f"{'='*80}\n")
        
        return results


def main():
    """CLI entry point"""
    
    config = HTMLParserConfig()
    if not config.get_openai_key():
        print("❌ Error: OPENAI_API_KEY not set")
        sys.exit(1)
    
    pipeline = HTMLToJSONPipeline(config)
    
    if len(sys.argv) > 1:
        # Process specific file
        pdf_file = Path(sys.argv[1])
        if not pdf_file.exists():
            print(f"❌ File not found: {pdf_file}")
            sys.exit(1)
        pipeline.process_file(pdf_file)
    else:
        pipeline.process_all_files()


if __name__ == "__main__":
    main()
