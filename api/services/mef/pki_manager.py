import os
from typing import Dict, Any, Optional
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta
import logging

class PKIManager:
    """Manage Public Key Infrastructure for Internal Revenue Service Modernized e-File submissions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.key_size = 2048
        self.cert_validity_days = 365
        self.key_path = os.getenv('IRS_PRIVATE_KEY_PATH')
        self.cert_path = os.getenv('IRS_CERT_PATH')

    def generate_key_pair(self) -> tuple:
        """Generate RSA key pair"""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.key_size
            )
            public_key = private_key.public_key()
            return private_key, public_key
        except Exception as e:
            self.logger.error(f"Error generating key pair: {str(e)}")
            raise

    def generate_certificate(self, 
                           private_key: rsa.RSAPrivateKey,
                           organization_name: str) -> x509.Certificate:
        """Generate X.509 certificate"""
        try:
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
                x509.NameAttribute(NameOID.COMMON_NAME, f"{organization_name} Modernized e-File Certificate")
            ])

            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=self.cert_validity_days)
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True
            ).sign(private_key, hashes.SHA256())

            return cert
        except Exception as e:
            self.logger.error(f"Error generating certificate: {str(e)}")
            raise

    def save_credentials(self, 
                        private_key: rsa.RSAPrivateKey,
                        certificate: x509.Certificate) -> None:
        """Save private key and certificate"""
        try:
            # Save private key
            with open(self.key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            # Save certificate
            with open(self.cert_path, 'wb') as f:
                f.write(certificate.public_bytes(
                    encoding=serialization.Encoding.PEM
                ))
        except Exception as e:
            self.logger.error(f"Error saving credentials: {str(e)}")
            raise

    def load_credentials(self) -> tuple:
        """Load private key and certificate"""
        try:
            # Load private key
            with open(self.key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )

            # Load certificate
            with open(self.cert_path, 'rb') as f:
                certificate = x509.load_pem_x509_certificate(f.read())

            return private_key, certificate
        except Exception as e:
            self.logger.error(f"Error loading credentials: {str(e)}")
            raise

    def rotate_keys(self, organization_name: str) -> None:
        """Rotate keys and certificate"""
        try:
            # Generate new credentials
            private_key, _ = self.generate_key_pair()
            certificate = self.generate_certificate(private_key, organization_name)

            # Backup existing credentials
            if os.path.exists(self.key_path):
                os.rename(self.key_path, f"{self.key_path}.bak")
            if os.path.exists(self.cert_path):
                os.rename(self.cert_path, f"{self.cert_path}.bak")

            # Save new credentials
            self.save_credentials(private_key, certificate)
        except Exception as e:
            self.logger.error(f"Error rotating keys: {str(e)}")
            raise
