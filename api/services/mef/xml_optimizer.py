import gzip
import io
from typing import Dict, Any
from lxml import etree
import logging
from api.config.mef_config import MEF_CONFIG


class XMLOptimizer:
    """Optimize XML documents for IRS submissions"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.batch_size = MEF_CONFIG["TRANSMISSION"]["BATCH_SIZE"]
        self.max_file_size = MEF_CONFIG["VALIDATION"]["MAX_FILE_SIZE"]

    def optimize(self, xml_content: str) -> str:
        """Optimize XML content"""
        try:
            # Parse and pretty print XML to normalize structure
            parser = etree.XMLParser(remove_blank_text=True)
            root = etree.fromstring(xml_content.encode(), parser)

            # Minify XML
            minified = self._minify_xml(root)

            # Check if compression needed
            if len(minified.encode()) > self.max_file_size:
                return self._compress_xml(minified)

            return minified

        except Exception as e:
            self.logger.error(f"Error optimizing XML: {str(e)}")
            raise

    def _minify_xml(self, root: etree.Element) -> str:
        """Minify XML by removing unnecessary whitespace"""
        return etree.tostring(
            root, encoding="unicode", pretty_print=False, with_tail=False
        )

    def _compress_xml(self, xml_content: str) -> str:
        """Compress XML using GZIP"""
        try:
            buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode="wb") as gz:
                gz.write(xml_content.encode())
            return buffer.getvalue()
        except Exception as e:
            self.logger.error(f"Error compressing XML: {str(e)}")
            raise

    def batch_process(self, xml_documents: list) -> list:
        """Process multiple XML documents in batches"""
        try:
            batches = []
            current_batch = []
            current_size = 0

            for doc in xml_documents:
                doc_size = len(doc.encode())

                if current_size + doc_size > self.max_file_size:
                    batches.append(current_batch)
                    current_batch = [doc]
                    current_size = doc_size
                else:
                    current_batch.append(doc)
                    current_size += doc_size

            if current_batch:
                batches.append(current_batch)

            return [self.optimize("\n".join(batch)) for batch in batches]

        except Exception as e:
            self.logger.error(f"Error batch processing XML: {str(e)}")
            raise

    def create_stream_reader(self, file_path: str):
        """Create streaming XML reader for large files"""
        try:
            return etree.iterparse(
                file_path, events=("start", "end"), remove_blank_text=True
            )
        except Exception as e:
            self.logger.error(f"Error creating XML stream reader: {str(e)}")
            raise
