import pytest
from unittest.mock import Mock, patch
from api.services.mef.xml_signer import XMLSigner
from api.services.mef.pki_manager import PKIManager
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509


@pytest.fixture
def xml_signer():
    return XMLSigner()


@pytest.fixture
def mock_pki_manager():
    return Mock(spec=PKIManager)


class TestXMLSigner:

    def test_sign_xml(self, xml_signer, mock_pki_manager):
        # Test data
        test_xml = "<test>content</test>"

        # Mock private key and certificate
        mock_private_key = Mock(spec=rsa.RSAPrivateKey)
        mock_certificate = Mock(spec=x509.Certificate)

        # Configure mocks
        with patch.object(xml_signer, "pki_manager", mock_pki_manager):
            mock_pki_manager.load_credentials.return_value = (
                mock_private_key,
                mock_certificate,
            )
            mock_private_key.sign.return_value = b"test_signature"

            # Execute test
            signed_xml = xml_signer.sign_xml(test_xml)

            # Assertions
            assert "<Signature>" in signed_xml
            assert "<SignatureValue>" in signed_xml
            assert "<X509Certificate>" in signed_xml
            mock_private_key.sign.assert_called_once()

    def test_verify_signature(self, xml_signer):
        # Test data
        signed_xml = """
            <test>
                <content>test</content>
                <Signature>
                    <SignatureValue>test_signature</SignatureValue>
                    <X509Certificate>test_cert</X509Certificate>
                </Signature>
            </test>
        """

        # Execute test
        result = xml_signer.verify_signature(signed_xml)

        # Assertions
        assert isinstance(result, bool)

    def test_invalid_xml(self, xml_signer):
        # Test data
        invalid_xml = "not xml"

        # Execute test and assert
        with pytest.raises(Exception):
            xml_signer.sign_xml(invalid_xml)

    def test_missing_certificate(self, xml_signer, mock_pki_manager):
        # Test data
        test_xml = "<test>content</test>"

        # Mock PKI manager to simulate missing certificate
        with patch.object(xml_signer, "pki_manager", mock_pki_manager):
            mock_pki_manager.load_credentials.side_effect = FileNotFoundError

            # Execute test and assert
            with pytest.raises(Exception):
                xml_signer.sign_xml(test_xml)

    @pytest.mark.asyncio
    async def test_sign_xml_with_amendment(self, xml_signer, mock_pki_manager):
        # Test data for amendment
        amendment_xml = "<amendment>content</amendment>"

        # Mock private key and certificate
        mock_private_key = Mock(spec=rsa.RSAPrivateKey)
        mock_certificate = Mock(spec=x509.Certificate)

        # Configure mocks
        with patch.object(xml_signer, "pki_manager", mock_pki_manager):
            mock_pki_manager.load_credentials.return_value = (
                mock_private_key,
                mock_certificate,
            )
            mock_private_key.sign.return_value = b"amendment_signature"

            # Execute test
            signed_amendment_xml = xml_signer.sign_xml(amendment_xml)

            # Assertions
            assert "<Signature>" in signed_amendment_xml
            assert "<SignatureValue>" in signed_amendment_xml
            assert "<X509Certificate>" in signed_amendment_xml
            mock_private_key.sign.assert_called_once()
