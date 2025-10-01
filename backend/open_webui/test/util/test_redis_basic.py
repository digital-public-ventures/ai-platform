import pytest
from open_webui.utils.redis import (
    parse_redis_service_url,
    get_sentinels_from_env,
)


class TestRedisBasics:
    def test_parse_redis_service_url_valid(self):
        url = "redis://user:pass@mymaster:6379/0"
        result = parse_redis_service_url(url)
        assert result["username"] == "user"
        assert result["password"] == "pass"
        assert result["service"] == "mymaster"
        assert result["port"] == 6379
        assert result["db"] == 0

    def test_parse_redis_service_url_defaults(self):
        url = "redis://mymaster"
        result = parse_redis_service_url(url)
        assert result["username"] is None
        assert result["password"] is None
        assert result["service"] == "mymaster"
        assert result["port"] == 6379
        assert result["db"] == 0

    def test_parse_redis_service_url_invalid_scheme(self):
        with pytest.raises(ValueError, match="Invalid Redis URL scheme"):
            parse_redis_service_url("http://invalid")

    def test_get_sentinels_from_env(self):
        hosts = "sentinel1,sentinel2,sentinel3"
        port = "26379"
        result = get_sentinels_from_env(hosts, port)
        expected = [("sentinel1", 26379), ("sentinel2", 26379), ("sentinel3", 26379)]
        assert result == expected

    def test_get_sentinels_from_env_empty(self):
        result = get_sentinels_from_env(None, "26379")
        assert result == []

