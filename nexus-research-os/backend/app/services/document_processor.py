"""
Document Processing Service
Handles PDF parsing, text extraction, chunking strategies, and metadata extraction.
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiofiles
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
)
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
    CSVLoader,
    JSONLoader,
)
from langchain_core.documents import Document as LangChainDocument

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    TXT = "txt"
    MD = "markdown"
    DOCX = "docx"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    XML = "xml"


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""
    RECURSIVE = "recursive"
    CHARACTER = "character"
    TOKEN = "token"
    FIXED = "fixed"


@dataclass
class ChunkMetadata:
    """Metadata for a text chunk."""
    chunk_index: int
    start_char: int
    end_char: int
    content_length: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedChunk:
    """A processed text chunk with metadata."""
    content: str
    metadata: ChunkMetadata
    embedding_ready: bool = False


@dataclass
class DocumentProcessingResult:
    """Result of document processing."""
    success: bool
    text_content: str
    chunks: List[ProcessedChunk]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class BaseParser(ABC):
    """Abstract base class for document parsers."""
    
    @abstractmethod
    async def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Parse document and return text content and metadata."""
        pass
    
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        pass


class PDFParser(BaseParser):
    """PDF document parser using PyPDF and pdfplumber."""
    
    def supported_extensions(self) -> List[str]:
        return [".pdf"]
    
    async def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Parse PDF file and extract text with metadata."""
        try:
            # Use PyPDFLoader for robust PDF parsing
            loader = PyPDFLoader(file_path)
            documents = await asyncio.to_thread(loader.load)
            
            # Combine all pages
            full_text = "\n\n".join([doc.page_content for doc in documents])
            
            # Extract metadata
            metadata = {
                "page_count": len(documents),
                "file_type": "pdf",
            }
            
            # Try to extract additional metadata from first page
            if documents and hasattr(documents[0], 'metadata'):
                metadata.update(documents[0].metadata)
            
            return full_text, metadata
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            raise


class TextParser(BaseParser):
    """Plain text file parser."""
    
    def supported_extensions(self) -> List[str]:
        return [".txt", ".text"]
    
    async def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Parse plain text file."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            metadata = {
                "file_type": "text",
                "character_count": len(content),
                "line_count": content.count('\n') + 1,
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {str(e)}")
            raise


class MarkdownParser(BaseParser):
    """Markdown file parser."""
    
    def supported_extensions(self) -> List[str]:
        return [".md", ".markdown"]
    
    async def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Parse markdown file."""
        try:
            loader = UnstructuredMarkdownLoader(file_path)
            documents = await asyncio.to_thread(loader.load)
            
            content = "\n\n".join([doc.page_content for doc in documents])
            
            metadata = {
                "file_type": "markdown",
            }
            
            if documents and hasattr(documents[0], 'metadata'):
                metadata.update(documents[0].metadata)
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error parsing markdown {file_path}: {str(e)}")
            raise


class HTMLParser(BaseParser):
    """HTML file parser."""
    
    def supported_extensions(self) -> List[str]:
        return [".html", ".htm"]
    
    async def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Parse HTML file."""
        try:
            loader = UnstructuredHTMLLoader(file_path)
            documents = await asyncio.to_thread(loader.load)
            
            content = "\n\n".join([doc.page_content for doc in documents])
            
            metadata = {
                "file_type": "html",
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error parsing HTML {file_path}: {str(e)}")
            raise


class CSVParser(BaseParser):
    """CSV file parser."""
    
    def supported_extensions(self) -> List[str]:
        return [".csv"]
    
    async def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Parse CSV file."""
        try:
            loader = CSVLoader(file_path)
            documents = await asyncio.to_thread(loader.load)
            
            # Convert CSV rows to readable text
            content_parts = []
            for doc in documents:
                content_parts.append(doc.page_content)
            
            content = "\n".join(content_parts)
            
            metadata = {
                "file_type": "csv",
                "row_count": len(documents),
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error parsing CSV {file_path}: {str(e)}")
            raise


class JSONParser(BaseParser):
    """JSON file parser."""
    
    def supported_extensions(self) -> List[str]:
        return [".json"]
    
    async def parse(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Parse JSON file."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                import json
                data = json.loads(await f.read())
            
            # Convert JSON to readable text representation
            content = json.dumps(data, indent=2, ensure_ascii=False)
            
            metadata = {
                "file_type": "json",
                "keys": list(data.keys()) if isinstance(data, dict) else "array",
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Error parsing JSON {file_path}: {str(e)}")
            raise


class DocumentProcessor:
    """Main document processing service."""
    
    def __init__(
        self,
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.chunking_strategy = chunking_strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize parsers
        self.parsers: Dict[str, BaseParser] = {
            "pdf": PDFParser(),
            "txt": TextParser(),
            "md": MarkdownParser(),
            "html": HTMLParser(),
            "csv": CSVParser(),
            "json": JSONParser(),
        }
        
        # Initialize text splitters
        self._init_text_splitters()
    
    def _init_text_splitters(self):
        """Initialize text splitters based on strategy."""
        if self.chunking_strategy == ChunkingStrategy.RECURSIVE:
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
        elif self.chunking_strategy == ChunkingStrategy.CHARACTER:
            self.splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        elif self.chunking_strategy == ChunkingStrategy.TOKEN:
            self.splitter = TokenTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        else:
            # Default to recursive
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
    
    def get_parser(self, file_extension: str) -> BaseParser:
        """Get appropriate parser for file extension."""
        ext = file_extension.lower().lstrip('.')
        
        for parser in self.parsers.values():
            if f".{ext}" in parser.supported_extensions():
                return parser
        
        raise ValueError(f"No parser available for extension: {file_extension}")
    
    async def process_file(
        self,
        file_path: str,
        document_id: str,
        custom_metadata: Optional[Dict[str, Any]] = None,
    ) -> DocumentProcessingResult:
        """Process a document file end-to-end."""
        try:
            # Get file extension
            path = Path(file_path)
            ext = path.suffix.lower()
            
            # Get appropriate parser
            parser = self.get_parser(ext)
            
            # Parse document
            text_content, file_metadata = await parser.parse(file_path)
            
            # Calculate file hash for deduplication
            file_hash = await self._calculate_file_hash(file_path)
            
            # Merge metadata
            metadata = {
                "document_id": document_id,
                "file_name": path.name,
                "file_path": str(path),
                "file_extension": ext,
                "file_hash": file_hash,
                **file_metadata,
                **(custom_metadata or {}),
            }
            
            # Chunk the text
            chunks = await self._chunk_text(text_content, metadata)
            
            return DocumentProcessingResult(
                success=True,
                text_content=text_content,
                chunks=chunks,
                metadata=metadata,
                warnings=[],
            )
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return DocumentProcessingResult(
                success=False,
                text_content="",
                chunks=[],
                metadata={},
                error_message=str(e),
            )
    
    async def _chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any],
    ) -> List[ProcessedChunk]:
        """Split text into chunks with metadata."""
        try:
            # Use LangChain splitter
            langchain_docs = self.splitter.split_text(text)
            
            # Track character positions
            current_pos = 0
            chunks = []
            
            for idx, chunk_text in enumerate(langchain_docs):
                # Find position in original text
                start_pos = text.find(chunk_text, current_pos)
                if start_pos == -1:
                    start_pos = current_pos
                
                end_pos = start_pos + len(chunk_text)
                current_pos = end_pos
                
                chunk_metadata = ChunkMetadata(
                    chunk_index=idx,
                    start_char=start_pos,
                    end_char=end_pos,
                    content_length=len(chunk_text),
                    metadata={
                        **metadata,
                        "chunk_index": idx,
                        "total_chunks": len(langchain_docs),
                    },
                )
                
                chunks.append(ProcessedChunk(
                    content=chunk_text,
                    metadata=chunk_metadata,
                ))
            
            logger.info(f"Created {len(chunks)} chunks from text")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file for deduplication."""
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(4096):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def process_text_direct(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[ProcessedChunk]:
        """Process raw text directly without file I/O."""
        meta = {
            "document_id": document_id,
            "source_type": "raw_text",
            **(metadata or {}),
        }
        
        # Use asyncio event loop for consistency
        loop = asyncio.new_event_loop()
        try:
            chunks = loop.run_until_complete(self._chunk_text(text, meta))
        finally:
            loop.close()
        
        return chunks


# Singleton instance
_document_processor: Optional[DocumentProcessor] = None


def get_document_processor() -> DocumentProcessor:
    """Get or create document processor singleton."""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
