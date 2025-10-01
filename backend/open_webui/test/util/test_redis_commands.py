from unittest.mock import Mock, patch, AsyncMock
from open_webui.utils.redis import SentinelRedisProxy


class TestSentinelRedisProxyCommands:
    @patch("redis.sentinel.Sentinel")
    def test_hash_commands_sync(self, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_master.hset.return_value = 1
        mock_master.hget.return_value = "test_value"
        mock_master.hgetall.return_value = {"key1": "value1", "key2": "value2"}
        mock_master.hdel.return_value = 1
        mock_sentinel.master_for.return_value = mock_master
        proxy = SentinelRedisProxy(mock_sentinel, "mymaster", async_mode=False)
        assert proxy.__getattr__("hset")("test_hash", "field1", "value1") == 1
        assert proxy.__getattr__("hget")("test_hash", "field1") == "test_value"
        assert proxy.__getattr__("hgetall")("test_hash") == {"key1": "value1", "key2": "value2"}
        assert proxy.__getattr__("hdel")("test_hash", "field1") == 1

    @patch("redis.sentinel.Sentinel")
    async def test_hash_commands_async(self, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_master.hset = AsyncMock(return_value=1)
        mock_master.hget = AsyncMock(return_value="test_value")
        mock_master.hgetall = AsyncMock(return_value={"key1": "value1", "key2": "value2"})
        mock_sentinel.master_for.return_value = mock_master
        proxy = SentinelRedisProxy(mock_sentinel, "mymaster", async_mode=True)
        assert await proxy.__getattr__("hset")("test_hash", "field1", "value1") == 1
        assert await proxy.__getattr__("hget")("test_hash", "field1") == "test_value"
        assert await proxy.__getattr__("hgetall")("test_hash") == {"key1": "value1", "key2": "value2"}

