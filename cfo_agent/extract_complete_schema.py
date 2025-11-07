"""
Extract Complete Database Schema
This script queries your PostgreSQL database to get the complete schema
for all tables and views used by the CFO agent
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

from db.pool import db_pool
from db.whitelist import ALLOWED_SURFACES
from dotenv import load_dotenv

load_dotenv()


async def extract_schema():
    """Extract complete schema from database"""
    
    print("="*80)
    print("📊 EXTRACTING COMPLETE DATABASE SCHEMA")
    print("="*80)
    print(f"\nAllowed surfaces: {len(ALLOWED_SURFACES)}")
    print(f"Surfaces: {sorted(ALLOWED_SURFACES)}\n")
    
    schema_info = {}
    
    for surface in sorted(ALLOWED_SURFACES):
        print(f"Querying: {surface}...")
        
        try:
            # Query to get column information
            query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position;
            """
            
            columns = await db_pool.execute_query(query, {"table_name": surface})
            
            if columns:
                schema_info[surface] = {
                    "column_count": len(columns),
                    "columns": [
                        {
                            "name": col["column_name"],
                            "type": col["data_type"],
                            "nullable": col["is_nullable"] == "YES",
                            "default": col["column_default"]
                        }
                        for col in columns
                    ]
                }
                print(f"  ✅ Found {len(columns)} columns")
            else:
                print(f"  ⚠️  No columns found (might be in different schema)")
                
                # Try querying the view directly to get column names
                try:
                    sample_query = f"SELECT * FROM {surface} LIMIT 1"
                    sample_result = await db_pool.execute_query(sample_query, {})
                    
                    if sample_result and len(sample_result) > 0:
                        column_names = list(sample_result[0].keys())
                        schema_info[surface] = {
                            "column_count": len(column_names),
                            "columns": [
                                {
                                    "name": col,
                                    "type": "unknown",
                                    "nullable": True,
                                    "default": None
                                }
                                for col in column_names
                            ]
                        }
                        print(f"  ✅ Extracted {len(column_names)} columns from sample query")
                except Exception as e:
                    print(f"  ❌ Could not query view: {str(e)}")
                    schema_info[surface] = {
                        "column_count": 0,
                        "columns": [],
                        "error": str(e)
                    }
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            schema_info[surface] = {
                "column_count": 0,
                "columns": [],
                "error": str(e)
            }
    
    # Save to files
    output_dir = Path("schema_output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = output_dir / f"complete_schema_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(schema_info, f, indent=2, default=str)
    
    # Save Markdown
    md_file = output_dir / f"complete_schema_{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write("# 📊 COMPLETE DATABASE SCHEMA\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Surfaces:** {len(ALLOWED_SURFACES)}\n\n")
        f.write("---\n\n")
        
        # Group by type
        views = [s for s in ALLOWED_SURFACES if s.startswith('vw_')]
        mvs = [s for s in ALLOWED_SURFACES if s.startswith('mv_')]
        tables = [s for s in ALLOWED_SURFACES if not s.startswith('vw_') and not s.startswith('mv_')]
        
        f.write("## Summary\n\n")
        f.write(f"- **Views (vw_):** {len(views)}\n")
        f.write(f"- **Materialized Views (mv_):** {len(mvs)}\n")
        f.write(f"- **Tables:** {len(tables)}\n\n")
        f.write("---\n\n")
        
        # Write each surface
        for surface in sorted(ALLOWED_SURFACES):
            info = schema_info.get(surface, {})
            columns = info.get('columns', [])
            
            f.write(f"## {surface}\n\n")
            
            if 'error' in info:
                f.write(f"**Error:** {info['error']}\n\n")
            elif columns:
                f.write(f"**Columns:** {len(columns)}\n\n")
                
                # Write column table
                f.write("| Column Name | Data Type | Nullable |\n")
                f.write("|-------------|-----------|----------|\n")
                
                for col in columns:
                    nullable = "✅" if col.get('nullable') else "❌"
                    f.write(f"| {col['name']} | {col['type']} | {nullable} |\n")
                
                f.write("\n")
                
                # Write column list for prompt
                f.write("**Column List (for prompt):**\n")
                f.write("```\n")
                f.write(", ".join([col['name'] for col in columns]))
                f.write("\n```\n\n")
            else:
                f.write("**No columns found**\n\n")
            
            f.write("---\n\n")
    
    # Save simplified version for prompt
    prompt_file = output_dir / f"schema_for_prompt_{timestamp}.md"
    with open(prompt_file, 'w') as f:
        f.write("# 📋 SCHEMA FOR SQL GENERATION PROMPT\n\n")
        f.write("Copy this into your generative_sql_prompt.md file\n\n")
        f.write("---\n\n")
        
        for surface in sorted(ALLOWED_SURFACES):
            info = schema_info.get(surface, {})
            columns = info.get('columns', [])
            
            if columns:
                column_names = [col['name'] for col in columns]
                f.write(f"**{surface}**: {', '.join(column_names[:30])}")
                if len(column_names) > 30:
                    f.write(f" ... and {len(column_names) - 30} more")
                f.write("\n\n")
    
    print(f"\n{'='*80}")
    print("✅ Schema extraction complete!")
    print(f"{'='*80}")
    print(f"\nFiles saved:")
    print(f"  1. {json_file}")
    print(f"  2. {md_file}")
    print(f"  3. {prompt_file}")
    print(f"\nTotal surfaces processed: {len(schema_info)}")
    print(f"Surfaces with columns: {sum(1 for s in schema_info.values() if s.get('columns'))}")
    print(f"{'='*80}\n")
    
    return schema_info


if __name__ == "__main__":
    asyncio.run(extract_schema())
