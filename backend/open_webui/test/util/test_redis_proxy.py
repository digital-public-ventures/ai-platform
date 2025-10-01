from unittest.mock import Mock, patch, AsyncMock
import redis
from open_webui.utils.redis import (
    SentinelRedisProxy,
    get_redis_connection,
)


class TestSentinelRedisProxy:
    @patch("redis.sentinel.Sentinel")
    def test_sentinel_redis_proxy_sync_success(self, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_master.get.return_value = "test_value"
        mock_sentinel.master_for.return_value = mock_master

        proxy = SentinelRedisProxy(mock_sentinel, "mymaster", async_mode=False)
        get_method = proxy.__getattr__("get")
        result = get_method("test_key")
        assert result == "test_value"

    @patch("redis.sentinel.Sentinel")
    async def test_sentinel_redis_proxy_async_success(self, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_master.get = AsyncMock(return_value="test_value")
        mock_sentinel.master_for.return_value = mock_master

        proxy = SentinelRedisProxy(mock_sentinel, "mymaster", async_mode=True)
        get_method = proxy.__getattr__("get")
        result = await get_method("test_key")
        assert result == "test_value"

    @patch("redis.sentinel.Sentinel")
    def test_sentinel_redis_proxy_failover_retry(self, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_master.get.side_effect = [
            redis.exceptions.ConnectionError("Master down"),
            "test_value",
        ]
        mock_sentinel.master_for.return_value = mock_master

        proxy = SentinelRedisProxy(mock_sentinel, "mymaster", async_mode=False)
        get_method = proxy.__getattr__("get")
        result = get_method("test_key")
        assert result == "test_value"

    @patch("redis.sentinel.Sentinel")
    def test_sentinel_redis_proxy_max_retries_exceeded(self, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_master.get.side_effect = redis.exceptions.ConnectionError("Master down")
        mock_sentinel.master_for.return_value = mock_master

        proxy = SentinelRedisProxy(mock_sentinel, "mymaster", async_mode=False)
        get_method = proxy.__getattr__("get")
        try:
            get_method("test_key")
            assert False, "Expected ConnectionError"
        except redis.exceptions.ConnectionError:
            pass

    @patch("redis.sentinel.Sentinel")
    @patch("redis.from_url")
    def test_get_redis_connection_with_sentinel(self, mock_from_url, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_sentinel_class.return_value = mock_sentinel
        sentinels = [("sentinel1", 26379), ("sentinel2", 26379)]
        redis_url = "redis://user:pass@mymaster:6379/0"
        result = get_redis_connection(redis_url=redis_url, redis_sentinels=sentinels, async_mode=False)
        assert isinstance(result, SentinelRedisProxy)

    @patch("redis.Redis.from_url")
    def test_get_redis_connection_without_sentinel(self, mock_from_url):
        mock_redis = Mock()
        mock_from_url.return_value = mock_redis
        redis_url = "redis://localhost:6379/0"
        result = get_redis_connection(redis_url=redis_url, redis_sentinels=None, async_mode=False)
        assert result == mock_redis

