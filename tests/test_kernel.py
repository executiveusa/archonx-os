"""
Tests — Kernel lifecycle & task execution
"""

import pytest

from archonx.kernel import ArchonXKernel, KernelConfig


@pytest.fixture
def kernel() -> ArchonXKernel:
    config = KernelConfig(
        protocol_min_depth=3,
        protocol_preferred_depth=5,
        confidence_threshold=0.7,
    )
    return ArchonXKernel(config=config)


@pytest.mark.asyncio
async def test_kernel_boot(kernel: ArchonXKernel) -> None:
    await kernel.boot()
    assert kernel._booted is True
    assert len(kernel.registry) == 64
    assert len(kernel.white_crew.agents) == 32
    assert len(kernel.black_crew.agents) == 32


@pytest.mark.asyncio
async def test_kernel_shutdown(kernel: ArchonXKernel) -> None:
    await kernel.boot()
    await kernel.shutdown()
    assert kernel._booted is False


@pytest.mark.asyncio
async def test_execute_task_before_boot_raises(kernel: ArchonXKernel) -> None:
    with pytest.raises(RuntimeError, match="not been booted"):
        await kernel.execute_task({"type": "test"})


@pytest.mark.asyncio
async def test_execute_approved_task(kernel: ArchonXKernel) -> None:
    await kernel.boot()
    result = await kernel.execute_task({"type": "deployment", "complexity": "medium"})
    assert result["status"] == "completed"
    assert result["confidence"] >= 0.7


@pytest.mark.asyncio
async def test_execute_rejected_task(kernel: ArchonXKernel) -> None:
    await kernel.boot()
    result = await kernel.execute_task({})  # no type → rejected
    assert result["status"] == "rejected"
    assert "REQUEST_MORE_DATA" in result["reason"]
