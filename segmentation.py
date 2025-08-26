class DocumentChunk:
    def __init__(self, content, content_type, metadata):
        self.content = content  # Text content of the block
        self.content_type = content_type  # For example: 'paragraph', 'table', 'list', 'title'
        self.metadata = metadata  # Dictionary with info like {'source': 'doc.pdf', 'page': 4, 'headings': ['Chapter 1', 'Installation']}

def segment_document(document_path: str) -> list[DocumentChunk]:
    """
    Loads the document and splits it into logical, meaningful blocks.
    """
    # Step 1: Load the document
    doc_loader = get_document_loader(document_path)
    raw_elements = doc_loader.extract_elements() # Gets a list of blocks (text, tables, images)

    chunks = []
    current_headings = []
    
    # Step 2: Go through the extracted elements and classify them
    for element in raw_elements:
        metadata = {'source': document_path, 'page': element.page_number}
        
        # Detect and keep heading hierarchy
        if element.is_heading():
            # Update the "path" to the current context
            level = element.heading_level # For example: H1, H2
            current_headings = current_headings[:level-1]
            current_headings.append(element.text)
            content_type = 'title'
        
        elif element.is_table():
            # Convert tables to Markdown format for better readability for LLM
            content = element.to_markdown()
            content_type = 'table'

        elif element.is_list():
            # Lists are taken as one block
            content = element.text
            content_type = 'list'
        
        else: # Normal text/paragraph
            content = element.text
            content_type = 'paragraph'
            # We can split the paragraph if it is too long
            if len(content) > 1000: # Example limit
                # Split the text into smaller parts by sentences, keep metadata
                sub_chunks = split(content, metadata, current_headings)
                chunks.extend(sub_chunks)
                continue # Skip adding the original big block

    metadata['headings'] = current_headings.copy()
    chunk = DocumentChunk(content, content_type, metadata)
    chunks.append(chunk)

    # Step 3: Return the list of structured blocks
    return chunks