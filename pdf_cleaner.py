#!/usr/bin/env -S uv run
import fitz  # PyMuPDF
import argparse
import sys
import os

def process_pdf(input_path, target_string, replacement_text=None, dry_run=False):
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_clean{ext}"

    try:
        doc = fitz.open(input_path)
        total_links_removed = 0
        total_text_instances_removed = 0

        for page in doc:
            # --- PART 1: REMOVE LINKS AND THEIR ASSOCIATED TEXT ---
            links = page.get_links()
            link_rects = []  # Track link rectangles to redact

            for link in links:
                uri = link.get("uri", "")
                if target_string.lower() in uri.lower():
                    # Get the link's rectangle (the clickable area with text)
                    link_rect = link.get("from")
                    if link_rect:
                        link_rects.append(fitz.Rect(link_rect))
                    if not dry_run:
                        page.delete_link(link)
                    total_links_removed += 1

            # Redact the entire text area for each matching link
            for rect in link_rects:
                if not dry_run:
                    page.add_redact_annot(
                        rect,
                        text=replacement_text if replacement_text else "",
                        fill=(1, 1, 1),
                        text_color=(1, 0, 0)
                    )
                total_text_instances_removed += 1

            # --- PART 2: REDACT STANDALONE TEXT (not part of links) ---
            text_instances = page.search_for(target_string)

            for inst in text_instances:
                # Skip if this text is already covered by a link redaction
                if any(rect.intersects(inst) for rect in link_rects):
                    continue
                if not dry_run:
                    page.add_redact_annot(
                        inst,
                        text=replacement_text if replacement_text else "",
                        fill=(1, 1, 1),
                        text_color=(1, 0, 0)
                    )
                total_text_instances_removed += 1

            if not dry_run and (link_rects or text_instances):
                # This actually executes the removal and replacement
                page.apply_redactions()

        if dry_run:
            print(f"🔎 Dry Run Results for '{target_string}':")
            print(f"   - Links to be removed: {total_links_removed}")
            print(f"   - Text instances to be scrubbed: {total_text_instances_removed}")
        else:
            doc.save(output_path, garbage=3, deflate=True)
            doc.close()
            print(f"✅ Process Complete")
            print(f"   - Removed {total_links_removed} links.")
            print(f"   - Replaced {total_text_instances_removed} text instances with '{replacement_text or '[BLANK]'}'.")
            print(f"📁 Saved to: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Remove links and replace text in a PDF.")
    parser.add_argument("file", help="The source PDF file")
    parser.add_argument("pattern", help="The text/URL pattern to remove")
    parser.add_argument("-r", "--replace", help="Text to put in place of the removed text (e.g. '[REDACTED]')")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)

    process_pdf(args.file, args.pattern, replacement_text=args.replace, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
