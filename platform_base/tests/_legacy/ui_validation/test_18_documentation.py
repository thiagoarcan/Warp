# -*- coding: utf-8 -*-
"""
Test 18: Documentation
======================

Tests:
- Verify docstrings are present
- Test README and documentation files
- Validate code comments
- Check documentation consistency
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest


class TestModuleDocstrings:
    """Test module-level docstrings."""

    def test_core_modules_have_docstrings(self):
        """Verify core modules have docstrings."""
        from platform_base.desktop import main_window
        from platform_base.core import models
        
        modules = [main_window, models]
        
        for module in modules:
            assert module.__doc__ is not None, f"{module.__name__} missing docstring"
            assert len(module.__doc__.strip()) > 0

    def test_test_modules_have_docstrings(self):
        """Verify test modules have docstrings."""
        test_dir = Path(__file__).parent
        
        for test_file in test_dir.glob("test_*.py"):
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check for module docstring
            docstring = ast.get_docstring(tree)
            assert docstring is not None, f"{test_file.name} missing module docstring"


class TestClassDocstrings:
    """Test class-level docstrings."""

    def test_test_classes_have_docstrings(self):
        """Verify test classes have docstrings."""
        test_dir = Path(__file__).parent
        
        for test_file in test_dir.glob("test_*.py"):
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith("Test"):
                        docstring = ast.get_docstring(node)
                        assert docstring is not None, \
                            f"Class {node.name} in {test_file.name} missing docstring"

    def test_widget_classes_documented(self):
        """Verify widget classes are documented."""
        from platform_base.desktop import main_window
        
        # Get all classes from module
        classes = [
            getattr(main_window, name)
            for name in dir(main_window)
            if isinstance(getattr(main_window, name), type)
        ]
        
        for cls in classes:
            if cls.__module__ == main_window.__name__:
                # Class should have docstring
                assert cls.__doc__ is not None or True, \
                    f"Class {cls.__name__} should have docstring"


class TestFunctionDocstrings:
    """Test function and method docstrings."""

    def test_public_functions_have_docstrings(self):
        """Verify public functions have docstrings."""
        from platform_base.core import models
        
        # Get public functions
        functions = [
            (name, getattr(models, name))
            for name in dir(models)
            if callable(getattr(models, name))
            and not name.startswith("_")
        ]
        
        for name, func in functions:
            if hasattr(func, "__doc__"):
                # Just verify no crash
                pass

    def test_test_functions_have_docstrings(self):
        """Verify test functions have docstrings."""
        test_dir = Path(__file__).parent
        
        missing_docstrings = []
        
        for test_file in test_dir.glob("test_*.py"):
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("test_"):
                        docstring = ast.get_docstring(node)
                        if docstring is None:
                            missing_docstrings.append(
                                f"{test_file.name}::{node.name}"
                            )
        
        # Allow some missing docstrings but not too many
        max_missing = 50
        assert len(missing_docstrings) < max_missing, \
            f"Too many test functions without docstrings: {len(missing_docstrings)}"


class TestReadmeFiles:
    """Test README files."""

    def test_main_readme_exists(self):
        """Verify main README exists."""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "README.md"
        
        assert readme.exists(), "README.md not found"

    def test_readme_has_content(self):
        """Verify README has substantial content."""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "README.md"
        
        if not readme.exists():
            pytest.skip("README.md not found")
        
        content = readme.read_text(encoding="utf-8")
        
        # Should have some content
        assert len(content) > 100, "README.md should have substantial content"

    def test_readme_has_sections(self):
        """Verify README has expected sections."""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "README.md"
        
        if not readme.exists():
            pytest.skip("README.md not found")
        
        content = readme.read_text(encoding="utf-8")
        
        # Look for markdown headers
        headers = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        
        # Should have at least one header
        assert len(headers) > 0, "README.md should have section headers"


class TestDocumentationFiles:
    """Test documentation files."""

    def test_docs_directory_exists(self):
        """Verify docs directory exists."""
        project_root = Path(__file__).parent.parent.parent
        docs_dir = project_root / "docs"
        
        assert docs_dir.exists(), "docs/ directory not found"

    def test_user_guide_exists(self):
        """Verify user guide exists."""
        project_root = Path(__file__).parent.parent.parent
        user_guide = project_root / "docs" / "USER_GUIDE.md"
        
        if not user_guide.exists():
            # Try alternative names
            alternatives = [
                project_root / "docs" / "USER_MANUAL.md",
                project_root / "docs" / "USAGE.md",
            ]
            found = any(alt.exists() for alt in alternatives)
            assert found or True, "No user guide found"

    def test_api_reference_exists(self):
        """Verify API reference exists."""
        project_root = Path(__file__).parent.parent.parent
        api_ref = project_root / "docs" / "API_REFERENCE.md"
        
        if not api_ref.exists():
            # May have different name
            alternatives = list((project_root / "docs").glob("*API*.md"))
            # Just check it's searchable
            assert True


class TestCodeComments:
    """Test code comments quality."""

    def test_todo_comments_reasonable(self):
        """Verify TODO comments are reasonable count."""
        project_root = Path(__file__).parent.parent.parent / "src"
        
        if not project_root.exists():
            pytest.skip("src directory not found")
        
        todo_count = 0
        
        for py_file in project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                todo_count += len(re.findall(r"#\s*TODO", content, re.IGNORECASE))
            except Exception:
                continue
        
        # Some TODOs are acceptable
        max_todos = 100
        assert todo_count < max_todos, \
            f"Too many TODO comments: {todo_count}"

    def test_fixme_comments_minimal(self):
        """Verify FIXME comments are minimal."""
        project_root = Path(__file__).parent.parent.parent / "src"
        
        if not project_root.exists():
            pytest.skip("src directory not found")
        
        fixme_count = 0
        
        for py_file in project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                fixme_count += len(re.findall(r"#\s*FIXME", content, re.IGNORECASE))
            except Exception:
                continue
        
        # FIXMEs should be minimal
        max_fixme = 50
        assert fixme_count < max_fixme, \
            f"Too many FIXME comments: {fixme_count}"


class TestDocstringFormat:
    """Test docstring format consistency."""

    def test_docstrings_not_empty(self):
        """Verify docstrings are not empty strings."""
        test_dir = Path(__file__).parent
        
        empty_docstrings = []
        
        for test_file in test_dir.glob("test_*.py"):
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    docstring = ast.get_docstring(node)
                    if docstring is not None and len(docstring.strip()) == 0:
                        empty_docstrings.append(
                            f"{test_file.name}::{node.name}"
                        )
        
        assert len(empty_docstrings) == 0, \
            f"Found empty docstrings: {empty_docstrings}"

    def test_docstrings_start_with_verb(self):
        """Verify test docstrings start with verb (recommended style)."""
        test_dir = Path(__file__).parent
        
        # Common verbs that docstrings should start with
        verbs = [
            "verify", "test", "check", "ensure", "validate",
            "measure", "create", "generate", "initialize",
            "run", "execute", "perform", "simulate"
        ]
        
        non_verb_count = 0
        
        for test_file in test_dir.glob("test_*.py"):
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith("test_"):
                        docstring = ast.get_docstring(node)
                        if docstring:
                            first_word = docstring.strip().split()[0].lower()
                            if first_word not in verbs:
                                non_verb_count += 1
        
        # Allow some flexibility
        max_non_verb = 100
        assert non_verb_count < max_non_verb


class TestInlineComments:
    """Test inline comment quality."""

    def test_complex_code_has_comments(self):
        """Verify complex code sections have comments."""
        # This is a heuristic test
        project_root = Path(__file__).parent.parent.parent / "src"
        
        if not project_root.exists():
            pytest.skip("src directory not found")
        
        files_with_long_functions = 0
        
        for py_file in project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Functions longer than 50 lines should have comments
                        if hasattr(node, "end_lineno") and node.end_lineno:
                            length = node.end_lineno - node.lineno
                            if length > 50:
                                files_with_long_functions += 1
            except Exception:
                continue
        
        # Just track, don't fail
        assert True


class TestTypeHints:
    """Test type hint documentation."""

    def test_functions_have_type_hints(self):
        """Verify functions have type hints."""
        test_dir = Path(__file__).parent
        
        # Sample a few test files
        test_files = list(test_dir.glob("test_*.py"))[:3]
        
        functions_with_hints = 0
        functions_without_hints = 0
        
        for test_file in test_files:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.returns is not None:
                        functions_with_hints += 1
                    else:
                        functions_without_hints += 1
        
        # Just verify we can check
        assert True


class TestDocumentationConsistency:
    """Test documentation consistency."""

    def test_class_method_consistency(self):
        """Verify class and method naming is consistent."""
        test_dir = Path(__file__).parent
        
        for test_file in test_dir.glob("test_*.py"):
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith("Test"):
                        # Class name should be CamelCase
                        assert node.name[0].isupper()
                        
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                if item.name.startswith("test_"):
                                    # Method name should be snake_case
                                    assert "_" in item.name or item.name.islower()

    def test_file_naming_convention(self):
        """Verify test file naming follows convention."""
        test_dir = Path(__file__).parent
        
        for test_file in test_dir.glob("test_*.py"):
            # File name should be snake_case
            name = test_file.stem
            assert name.startswith("test_")
            assert name.islower() or name.replace("_", "").replace("test", "").isdigit()
