import pytest
import pytest_asyncio
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from arcreactor.core.managers.plugin_manager import PluginManager, PluginType

class TestDashboardPluginIntegration:
    @pytest_asyncio.fixture
    async def manager(self):
        # Ensure src is in sys.path
        import sys
        src_path = os.path.abspath("src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            
        # Scan the real source plugins directory
        plugin_dir = os.path.abspath("src/arcreactor/plugins")
        print(f"Scanning plugins in: {plugin_dir}")
        manager = PluginManager(plugin_dir=plugin_dir)
        await manager.load_plugins()
        return manager

    @pytest.mark.asyncio
    async def test_dashboard_plugin_loading(self, manager):
        # Verify dashboard plugin discovered and loaded
        manifests = manager.get_all_plugins()
        print(f"Loaded plugins: {[m.name for m in manifests]}")
        
        dashboard = manager.get_plugin("ui-dashboard")
        assert dashboard is not None, "ui-dashboard plugin not found"
        assert dashboard.manifest.type == PluginType.UI

    @pytest.mark.asyncio
    async def test_dashboard_serving(self, manager):
        dashboard = manager.get_plugin("ui-dashboard")
        assert dashboard is not None
        
        app = FastAPI()
        app.include_router(dashboard.get_router(), prefix="/dashboard")
        client = TestClient(app)
        
        # Verify index.html is served
        response = client.get("/dashboard/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        # Basic check for content if possible, though index.html might be minimal or empty in dev
        
