from api.routes.auth_routes import generate_otp


def test_otp_generation():
    """Test if OTP is a 6-digit number."""
    otp = generate_otp()
    assert len(otp) == 6 and otp.isdigit(), "OTP is not a valid 6-digit number."
