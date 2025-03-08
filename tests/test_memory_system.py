import os
import tempfile

def test_basic_memory_creation():
    """Simplest possible test for memory system creation"""
    from agents.memory_system import AutonomosMemorySystem
    memory = AutonomosMemorySystem()
    memory.add_context("Test context")
    assert len(memory.conversation_history) == 1

def test_hybrid_memory_basic():
    """Basic test for hybrid memory system with minimal initialization"""
    from agents.memory_system import HybridMemorySystem
    
    # Use a temporary directory to avoid persistent storage overhead
    with tempfile.TemporaryDirectory() as tmpdir:
        # Disable vector index and embedding model
        os.environ['DISABLE_VECTOR_INDEX'] = 'true'
        
        memory = HybridMemorySystem()
        memory.add_context("Autonomos AI memory test")
        
        # Basic assertions
        assert memory.token_usage >= 0
        assert len(memory.llama_memory.get_all()) > 0
        
        # Clean up environment variable
        del os.environ['DISABLE_VECTOR_INDEX']
