#!/usr/bin/env python3
"""
Test script to validate the agent structure and JSON payloads.
This script tests the agent without requiring API keys or external services.
"""

import json
import sys
from pathlib import Path


def test_json_files():
    """Test that all JSON example files are valid and well-formed."""
    print("Testing JSON files...")
    
    json_files = ["example_simple.json", "example_with_mcp.json"]
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Validate structure
            assert "config" in data, f"{json_file}: Missing 'config' field"
            assert "task" in data, f"{json_file}: Missing 'task' field"
            
            config = data["config"]
            assert "model" in config, f"{json_file}: Missing 'config.model' field"
            assert "max_tokens" in config, f"{json_file}: Missing 'config.max_tokens' field"
            assert "mcp_servers" in config, f"{json_file}: Missing 'config.mcp_servers' field"
            
            print(f"  ✓ {json_file} - Valid")
            print(f"    Task: {data['task'][:60]}...")
            print(f"    Model: {config['model']}")
            print(f"    MCP Servers: {len(config['mcp_servers'])}")
        except Exception as e:
            print(f"  ✗ {json_file} - Error: {e}")
            return False
    
    return True


def test_python_syntax():
    """Test that the Python agent file has valid syntax."""
    print("\nTesting Python syntax...")
    
    try:
        with open('agent.py', 'r') as f:
            code = f.read()
        
        compile(code, 'agent.py', 'exec')
        print("  ✓ agent.py - Valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"  ✗ agent.py - Syntax Error: {e}")
        return False


def test_requirements():
    """Test that requirements.txt exists and contains expected packages."""
    print("\nTesting requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        required_packages = ["anthropic", "mcp", "pydantic", "python-dotenv"]
        
        for package in required_packages:
            if package in requirements:
                print(f"  ✓ {package} - Found")
            else:
                print(f"  ✗ {package} - Missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error reading requirements.txt: {e}")
        return False


def test_documentation():
    """Test that documentation exists and is complete."""
    print("\nTesting documentation...")
    
    try:
        with open('README.md', 'r') as f:
            readme = f.read()
        
        required_sections = [
            "Installation",
            "Usage",
            "JSON Payload Structure",
            "Examples"
        ]
        
        for section in required_sections:
            if section in readme:
                print(f"  ✓ {section} section - Found")
            else:
                print(f"  ✗ {section} section - Missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error reading README.md: {e}")
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("Generic Agent Validation Tests")
    print("="*80)
    
    results = []
    
    results.append(("JSON Files", test_json_files()))
    results.append(("Python Syntax", test_python_syntax()))
    results.append(("Requirements", test_requirements()))
    results.append(("Documentation", test_documentation()))
    
    print("\n" + "="*80)
    print("Test Results Summary")
    print("="*80)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*80)
    
    if all_passed:
        print("\n✓ All tests passed! The agent is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set your API key: export ANTHROPIC_API_KEY='your-key'")
        print("3. Run the agent: python agent.py example_simple.json")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
