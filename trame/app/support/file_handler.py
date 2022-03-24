"""
doc
"""
import jwt


class FileHandler:
    """doc"""

    @staticmethod
    def get_user_name(request, dev):
        """doc"""
        if dev:
            return "dev"

        encoded_token = request.headers.get("Authorization")
        if encoded_token is None or encoded_token == "":
            return "guest"

        decoded_token = jwt.decode(
            encoded_token.split(" ")[1], options={"verify_signature": False}
        )

        return decoded_token["preferred_username"]
