from typing import Dict, Any
import xml.etree.ElementTree as ElementTree
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import b64encode, b64decode
import logging
from .pki_manager import PKIManager
from cryptography import x509

class XMLSigner:
    """Sign XML documents for IRS submissions"""
    
    def __init__(self):
        self.pki_manager = PKIManager()
        self.logger = logging.getLogger(__name__)

    def sign_xml(self, xml_content: str) -> str:
        """Sign XML content"""
        try:
            # Load credentials
            private_key, certificate = self.pki_manager.load_credentials()

            # Parse XML
            root = ElementTree.fromstring(xml_content)

            # Calculate document digest
            digest = hashes.Hash(hashes.SHA256())
            digest.update(xml_content.encode())
            digest_value = digest.finalize()

            # Sign the digest
            signature = private_key.sign(
                digest_value,
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            # Add signature to XML
            sig_element = ElementTree.SubElement(root, 'Signature')
            sig_value = ElementTree.SubElement(sig_element, 'SignatureValue')
            sig_value.text = b64encode(signature).decode()

            # Add certificate
            cert_element = ElementTree.SubElement(sig_element, 'X509Certificate')
            cert_element.text = b64encode(
                certificate.public_bytes(encoding=x509.Encoding.DER)
            ).decode()

            return ElementTree.tostring(root, encoding='unicode')
        except Exception as e:
            self.logger.error(f"Error signing XML: {str(e)}")
            raise

    def verify_signature(self, signed_xml: str) -> bool:
        """Verify XML signature"""
        try:
            root = ElementTree.fromstring(signed_xml)
            
            # Extract signature and certificate
            sig_element = root.find('Signature')
            if sig_element is None:
                return False

            signature = b64decode(sig_element.find('SignatureValue').text)
            cert_data = b64decode(sig_element.find('X509Certificate').text)
            
            # Load certificate
            certificate = x509.load_der_x509_certificate(cert_data)
            public_key = certificate.public_key()

            # Remove signature for digest calculation
            root.remove(sig_element)
            xml_without_sig = ElementTree.tostring(root, encoding='unicode')

            # Calculate digest
            digest = hashes.Hash(hashes.SHA256())
            digest.update(xml_without_sig.encode())
            digest_value = digest.finalize()

            # Verify signature
            try:
                public_key.verify(
                    signature,
                    digest_value,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                return True
            except:
                return False

        except Exception as e:
            self.logger.error(f"Error verifying signature: {str(e)}")
            return False
