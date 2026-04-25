"""DiscordNotifier URL validation (NIT #3 정정 검증)."""
from __future__ import annotations

import pytest

from engine.notifier import DiscordNotifier


VALID = "https://discord.com/api/webhooks/123456789012345678/" + "x" * 60


class TestUrlValidation:
    def test_valid_url_accepted(self):
        notif = DiscordNotifier(VALID)
        assert notif.webhook_url == VALID

    def test_empty_rejected(self):
        with pytest.raises(ValueError, match="prefix"):
            DiscordNotifier("")

    def test_wrong_prefix_rejected(self):
        with pytest.raises(ValueError, match="prefix"):
            DiscordNotifier("https://example.com/webhook/abc")

    def test_short_token_rejected(self):
        with pytest.raises(ValueError, match="path"):
            DiscordNotifier("https://discord.com/api/webhooks/123/abc")

    def test_non_digit_id_rejected(self):
        with pytest.raises(ValueError, match="path"):
            DiscordNotifier("https://discord.com/api/webhooks/notdigits/" + "x" * 60)

    def test_extra_path_segments_rejected(self):
        with pytest.raises(ValueError, match="path"):
            DiscordNotifier(
                "https://discord.com/api/webhooks/123456789012345678/" + "x" * 60 + "/extra"
            )
