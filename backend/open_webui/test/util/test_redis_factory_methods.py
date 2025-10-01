from unittest.mock import Mock, patch
from open_webui.utils.redis import SentinelRedisProxy
import inspect


class TestSentinelRedisProxyFactoryMethods:
    @patch("redis.sentinel.Sentinel")
    async def test_pubsub_factory_method_async(self, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_pubsub = Mock()
        mock_master.pubsub.return_value = mock_pubsub
        mock_sentinel.master_for.return_value = mock_master
        proxy = SentinelRedisProxy(mock_sentinel, "mymaster", async_mode=True)
        pubsub_method = proxy.__getattr__("pubsub")
        result = pubsub_method()
        assert result == mock_pubsub
        assert not inspect.iscoroutine(result)

    @patch("redis.sentinel.Sentinel")
    async def test_pipeline_factory_method_async(self, mock_sentinel_class):
        mock_sentinel = Mock()
        mock_master = Mock()
        mock_pipeline = Mock()
        mock_master.pipeline.return_value = mock_pipeline
        mock_pipeline.set.return_value = mock_pipeline
        mock_pipeline.get.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [True, "test_value"]
        mock_sentinel.master_for.return_value = mock_master
        proxy = SentinelRedisProxy(mock_sentinel, "mymaster", async_mode=True)
        pipeline_method = proxy.__getattr__("pipeline")
        result = pipeline_method()
        assert result == mock_pipeline
        assert not inspect.iscoroutine(result)

