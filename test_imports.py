import os
import sys

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def test_imports():
    print("=== Testing DSS Project Imports ===")
    print(f"Working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    
    # Test 1: simulation_events
    try:
        from simulation.simulation_events import Event, EventType
        print("✓ SUCCESS: simulation.simulation_events imported")
    except ImportError as e:
        print(f"✗ FAILED: simulation.simulation_events - {e}")
    
    # Test 2: simulation
    try:
        from simulation.simulation import EventDrivenSimulator
        print("✓ SUCCESS: simulation.simulation imported")
    except ImportError as e:
        print(f"✗ FAILED: simulation.simulation - {e}")
    
    # Test 3: base_node
    try:
        from nodes.base_node import Node
        print("✓ SUCCESS: nodes.base_node imported")
    except ImportError as e:
        print(f"✗ FAILED: nodes.base_node - {e}")
    
    # Test 4: raft_node
    try:
        from nodes.raft_node import RaftNode
        print("✓ SUCCESS: nodes.raft_node imported")
    except ImportError as e:
        print(f"✗ FAILED: nodes.raft_node - {e}")
    
    # Test 5: Check __init__.py files
    print("\n=== Checking __init__.py files ===")
    init_files = [
        "__init__.py",
        "simulation/__init__.py", 
        "nodes/__init__.py"
    ]
    
    for init_file in init_files:
        if os.path.exists(init_file):
            print(f"✓ {init_file} exists")
        else:
            print(f"✗ {init_file} missing - CREATE THIS FILE!")
    
    # Test 6: Full integration test
    print("\n=== Integration Test ===")
    try:
        from simulation.simulation import EventDrivenSimulator
        from nodes.raft_node import RaftNode
        
        # This would normally require a proper simulation class
        # but we're just testing imports
        print("✓ All imports work together!")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
    
    print("\n=== Directory Structure ===")
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.py'):
                print(f"{subindent}{file}")

if __name__ == "__main__":
    test_imports()