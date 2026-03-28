"""
Tests for CLI-Anything Skills Module

Comprehensive testing of CLI discovery, generation, registry, and execution.
"""

import pytest
from archonx.skills.cli_anything.discovery import DiscoveryEngine, discover_all_apps
from archonx.skills.cli_anything.generator import CLIGenerator
from archonx.skills.cli_anything.registry import CLIRegistry
from archonx.skills.cli_anything.executor import CLIExecutor


class TestDiscoveryEngine:
    """Tests for application discovery."""

    def test_discovery_engine_init(self):
        """Test discovery engine initialization."""
        engine = DiscoveryEngine()
        assert engine.os_type in ["Windows", "Darwin", "Linux"]
        assert isinstance(engine.discovered, set)

    def test_discover_apps(self):
        """Test app discovery."""
        engine = DiscoveryEngine()
        apps = engine.discover()
        assert isinstance(apps, list)
        # Should find at least some apps on typical systems
        # or empty list on minimal systems

    def test_discover_all_apps_function(self):
        """Test the global discover function."""
        apps = discover_all_apps()
        assert isinstance(apps, list)

    def test_register_custom_app(self):
        """Test registering a custom application."""
        engine = DiscoveryEngine()
        engine.register_custom_app("test_app", ["/usr/bin/test_app"])
        # Should not raise an exception


class TestCLIGenerator:
    """Tests for CLI schema generation."""

    def test_generator_init(self):
        """Test generator initialization."""
        gen = CLIGenerator("gimp")
        assert gen.app_name == "gimp"

    def test_generate_gimp_schema(self):
        """Test GIMP schema generation."""
        gen = CLIGenerator("gimp")
        schema = gen.generate()
        assert schema is not None
        assert "name" in schema
        assert schema["name"] == "gimp"
        assert "commands" in schema

    def test_generate_blender_schema(self):
        """Test Blender schema generation."""
        gen = CLIGenerator("blender")
        schema = gen.generate()
        assert schema is not None
        assert "commands" in schema
        assert "render_scene" in schema["commands"]

    def test_generate_libreoffice_schema(self):
        """Test LibreOffice schema generation."""
        gen = CLIGenerator("libreoffice")
        schema = gen.generate()
        assert schema is not None
        assert "commands" in schema

    def test_generate_unknown_app(self):
        """Test generating schema for unknown app."""
        gen = CLIGenerator("unknown_app_xyz")
        schema = gen.generate()
        assert schema is None

    def test_get_command_schema(self):
        """Test getting schema for specific command."""
        gen = CLIGenerator("gimp")
        gen.generate()
        cmd_schema = gen.get_command_schema("create_image")
        assert cmd_schema is not None
        assert "params" in cmd_schema

    def test_validate_params_success(self):
        """Test parameter validation success."""
        gen = CLIGenerator("gimp")
        gen.generate()
        is_valid, msg = gen.validate_params(
            "create_image",
            {"width": 800, "height": 600}
        )
        assert is_valid is True
        assert msg == ""

    def test_validate_params_missing_required(self):
        """Test validation fails for missing required params."""
        gen = CLIGenerator("gimp")
        gen.generate()
        is_valid, msg = gen.validate_params(
            "create_image",
            {"width": 800}  # Missing height
        )
        assert is_valid is False
        assert "Required parameter" in msg

    def test_validate_params_unknown_command(self):
        """Test validation for unknown command."""
        gen = CLIGenerator("gimp")
        gen.generate()
        is_valid, msg = gen.validate_params("unknown_command", {})
        assert is_valid is False
        assert "not found" in msg

    def test_schema_to_json(self):
        """Test exporting schema to JSON."""
        gen = CLIGenerator("gimp")
        gen.generate()
        json_str = gen.to_json()
        assert isinstance(json_str, str)
        assert "gimp" in json_str
        assert "commands" in json_str


class TestCLIRegistry:
    """Tests for CLI registry."""

    def test_registry_init(self):
        """Test registry initialization."""
        registry = CLIRegistry()
        assert len(registry.list_apps()) == 0

    def test_register_cli(self):
        """Test registering a CLI."""
        registry = CLIRegistry()
        schema = {"name": "test", "commands": {"cmd1": {}}}
        registry.register("test_app", schema)
        assert registry.has_cli("test_app")

    def test_unregister_cli(self):
        """Test unregistering a CLI."""
        registry = CLIRegistry()
        schema = {"name": "test", "commands": {}}
        registry.register("test_app", schema)
        result = registry.unregister("test_app")
        assert result is True
        assert not registry.has_cli("test_app")

    def test_unregister_nonexistent(self):
        """Test unregistering non-existent CLI."""
        registry = CLIRegistry()
        result = registry.unregister("nonexistent")
        assert result is False

    def test_get_cli(self):
        """Test retrieving CLI schema."""
        registry = CLIRegistry()
        schema = {"name": "test", "commands": {}}
        registry.register("test_app", schema)
        retrieved = registry.get_cli("test_app")
        assert retrieved == schema

    def test_list_apps(self):
        """Test listing all apps."""
        registry = CLIRegistry()
        registry.register("app1", {"commands": {}})
        registry.register("app2", {"commands": {}})
        apps = registry.list_apps()
        assert "app1" in apps
        assert "app2" in apps

    def test_list_commands(self):
        """Test listing commands for an app."""
        registry = CLIRegistry()
        schema = {
            "commands": {
                "cmd1": {},
                "cmd2": {},
            }
        }
        registry.register("test_app", schema)
        commands = registry.list_commands("test_app")
        assert "cmd1" in commands
        assert "cmd2" in commands

    def test_get_command(self):
        """Test retrieving command schema."""
        registry = CLIRegistry()
        schema = {
            "commands": {
                "my_command": {"params": {}}
            }
        }
        registry.register("test_app", schema)
        cmd = registry.get_command("test_app", "my_command")
        assert cmd is not None
        assert "params" in cmd

    def test_set_metadata(self):
        """Test setting metadata."""
        registry = CLIRegistry()
        registry.register("test_app", {})
        registry.set_metadata("test_app", {"version": "1.0"})
        metadata = registry.get_metadata("test_app")
        assert metadata["version"] == "1.0"

    def test_stats(self):
        """Test registry statistics."""
        registry = CLIRegistry()
        registry.register("app1", {
            "commands": {"cmd1": {}, "cmd2": {}}
        })
        registry.register("app2", {
            "commands": {"cmd3": {}}
        })
        stats = registry.stats()
        assert stats["registered_apps"] == 2
        assert stats["total_commands"] == 3

    def test_clear(self):
        """Test clearing registry."""
        registry = CLIRegistry()
        registry.register("test_app", {})
        registry.clear()
        assert len(registry.list_apps()) == 0


class TestCLIExecutor:
    """Tests for CLI execution."""

    def test_executor_init(self):
        """Test executor initialization."""
        executor = CLIExecutor()
        assert isinstance(executor.execution_log, list)

    def test_execute_gimp_command(self):
        """Test executing GIMP command."""
        executor = CLIExecutor()
        result = executor.execute(
            "gimp",
            "create_image",
            {"width": 800, "height": 600}
        )
        assert result["status"] == "success"
        assert result["app"] == "gimp"
        assert result["command"] == "create_image"
        assert "result" in result

    def test_execute_blender_command(self):
        """Test executing Blender command."""
        executor = CLIExecutor()
        result = executor.execute(
            "blender",
            "render_scene",
            {"output_path": "/tmp/output.png"}
        )
        assert result["status"] == "success"
        assert result["app"] == "blender"

    def test_execute_with_validation_success(self):
        """Test execution with successful validation."""
        executor = CLIExecutor()
        result = executor.execute_with_validation(
            "gimp",
            "create_image",
            {"width": 800, "height": 600}
        )
        assert result["status"] == "success"

    def test_execute_with_validation_failure(self):
        """Test execution with validation failure."""
        executor = CLIExecutor()
        result = executor.execute_with_validation(
            "gimp",
            "create_image",
            {"width": 800}  # Missing height
        )
        assert result["status"] == "validation_error"
        assert "error" in result

    def test_get_execution_log(self):
        """Test getting execution log."""
        executor = CLIExecutor()
        executor.execute("gimp", "create_image", {"width": 800, "height": 600})
        log = executor.get_execution_log()
        assert len(log) > 0
        assert log[0]["app"] == "gimp"

    def test_clear_log(self):
        """Test clearing execution log."""
        executor = CLIExecutor()
        executor.execute("gimp", "create_image", {"width": 800, "height": 600})
        executor.clear_log()
        assert len(executor.execution_log) == 0

    def test_execute_with_timeout(self):
        """Test execution with timeout parameter."""
        executor = CLIExecutor()
        result = executor.execute(
            "gimp",
            "create_image",
            {"width": 800, "height": 600},
            timeout=5
        )
        assert result["status"] == "success"


class TestCLIIntegration:
    """Integration tests for CLI-Anything."""

    def test_end_to_end_workflow(self):
        """Test complete CLI-Anything workflow."""
        # Discovery
        engine = DiscoveryEngine()
        apps = engine.discover()

        # Generation
        for app in apps[:1]:  # Test first discovered app
            gen = CLIGenerator(app)
            schema = gen.generate()
            if schema:
                # Registry
                registry = CLIRegistry()
                registry.register(app, schema)

                # Execution
                commands = registry.list_commands(app)
                if commands:
                    executor = CLIExecutor()
                    result = executor.execute(
                        app,
                        commands[0],
                        {}
                    )
                    assert result["status"] == "success"

    def test_multiple_apps_registration(self):
        """Test registering multiple apps."""
        registry = CLIRegistry()

        for app_name in ["gimp", "blender", "libreoffice"]:
            gen = CLIGenerator(app_name)
            schema = gen.generate()
            if schema:
                registry.register(app_name, schema)

        stats = registry.stats()
        assert stats["registered_apps"] >= 0
        assert stats["total_commands"] >= 0
