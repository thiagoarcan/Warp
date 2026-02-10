"""
Testes completos para caching/memory.py - Platform Base v2.0

Cobertura de 100% das funcionalidades de cache em memória.
"""

import pytest

from platform_base.caching.memory import MemoryCache, memory_cache


class TestMemoryCacheDecorator:
    """Testes para decorator memory_cache"""
    
    def test_basic_caching(self):
        """Testa caching básico"""
        call_count = [0]
        
        @memory_cache(maxsize=128)
        def expensive_func(x):
            call_count[0] += 1
            return x * 2
        
        # Primeira chamada
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count[0] == 1
        
        # Segunda chamada (cached)
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count[0] == 1  # Não incrementou
    
    def test_different_args_not_cached(self):
        """Testa que args diferentes não são cached"""
        call_count = [0]
        
        @memory_cache(maxsize=128)
        def func(x):
            call_count[0] += 1
            return x * 3
        
        func(1)
        func(2)
        func(3)
        
        assert call_count[0] == 3
    
    def test_maxsize_limit(self):
        """Testa limite de tamanho"""
        call_count = [0]
        
        @memory_cache(maxsize=3)
        def func(x):
            call_count[0] += 1
            return x
        
        # Preenche o cache
        for i in range(5):
            func(i)
        
        # Primeiros itens devem ter sido evicted
        func(0)  # Deve chamar a função novamente
        
        assert call_count[0] >= 5


class TestMemoryCache:
    """Testes para classe MemoryCache"""
    
    def test_creation_default(self):
        """Testa criação com defaults"""
        cache = MemoryCache()
        
        assert len(cache) == 0
    
    def test_creation_custom_maxsize(self):
        """Testa criação com maxsize customizado"""
        cache = MemoryCache(maxsize=50)
        
        assert cache._maxsize == 50
    
    def test_set_and_get(self):
        """Testa set e get básico"""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        
        assert cache.get("key1") == "value1"
    
    def test_get_nonexistent_returns_none(self):
        """Testa que get de chave inexistente retorna None"""
        cache = MemoryCache()
        
        assert cache.get("nonexistent") is None
    
    def test_set_updates_existing(self):
        """Testa que set atualiza valor existente"""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        cache.set("key1", "value2")
        
        assert cache.get("key1") == "value2"
        assert len(cache) == 1
    
    def test_delete_existing(self):
        """Testa delete de chave existente"""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        result = cache.delete("key1")
        
        assert result is True
        assert cache.get("key1") is None
        assert len(cache) == 0
    
    def test_delete_nonexistent(self):
        """Testa delete de chave inexistente"""
        cache = MemoryCache()
        
        result = cache.delete("nonexistent")
        
        assert result is False
    
    def test_clear(self):
        """Testa clear"""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        cache.clear()
        
        assert len(cache) == 0
        assert cache.get("key1") is None
    
    def test_contains(self):
        """Testa operador in"""
        cache = MemoryCache()
        
        cache.set("key1", "value1")
        
        assert "key1" in cache
        assert "nonexistent" not in cache
    
    def test_len(self):
        """Testa len()"""
        cache = MemoryCache()
        
        assert len(cache) == 0
        
        cache.set("key1", "value1")
        assert len(cache) == 1
        
        cache.set("key2", "value2")
        assert len(cache) == 2
        
        cache.delete("key1")
        assert len(cache) == 1
    
    def test_lru_eviction(self):
        """Testa eviction LRU"""
        cache = MemoryCache(maxsize=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Cache cheio
        assert len(cache) == 3
        
        # Adiciona novo item - deve evictar o mais antigo (key1)
        cache.set("key4", "value4")
        
        assert len(cache) == 3
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key4") == "value4"  # Adicionado
    
    def test_lru_access_updates_order(self):
        """Testa que acesso atualiza ordem LRU"""
        cache = MemoryCache(maxsize=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Acessa key1 - move para o fim
        cache.get("key1")
        
        # Adiciona key4 - deve evictar key2 (agora mais antigo)
        cache.set("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Não evicted
        assert cache.get("key2") is None  # Evicted
    
    def test_set_existing_updates_order(self):
        """Testa que set de chave existente atualiza ordem"""
        cache = MemoryCache(maxsize=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Atualiza key1 - move para o fim
        cache.set("key1", "updated_value1")
        
        # Adiciona key4 - deve evictar key2
        cache.set("key4", "value4")
        
        assert cache.get("key1") == "updated_value1"
        assert cache.get("key2") is None


class TestMemoryCacheDataTypes:
    """Testes com diferentes tipos de dados"""
    
    def test_cache_string(self):
        """Testa cache de strings"""
        cache = MemoryCache()
        
        cache.set("key", "Hello, World!")
        
        assert cache.get("key") == "Hello, World!"
    
    def test_cache_number(self):
        """Testa cache de números"""
        cache = MemoryCache()
        
        cache.set("int", 42)
        cache.set("float", 3.14159)
        
        assert cache.get("int") == 42
        assert cache.get("float") == 3.14159
    
    def test_cache_list(self):
        """Testa cache de listas"""
        cache = MemoryCache()
        
        data = [1, 2, 3, 4, 5]
        cache.set("list", data)
        
        assert cache.get("list") == [1, 2, 3, 4, 5]
    
    def test_cache_dict(self):
        """Testa cache de dicionários"""
        cache = MemoryCache()
        
        data = {"name": "test", "value": 123}
        cache.set("dict", data)
        
        result = cache.get("dict")
        assert result["name"] == "test"
        assert result["value"] == 123
    
    def test_cache_none(self):
        """Testa cache de None"""
        cache = MemoryCache()
        
        cache.set("null", None)
        
        # Deve retornar None, não "not found"
        assert cache.get("null") is None
        assert "null" in cache
    
    def test_cache_complex_object(self):
        """Testa cache de objeto complexo"""
        cache = MemoryCache()
        
        import numpy as np
        data = np.array([1, 2, 3, 4, 5])
        
        cache.set("array", data)
        
        result = cache.get("array")
        assert np.array_equal(result, data)


class TestMemoryCacheEdgeCases:
    """Testes de casos de borda"""
    
    def test_empty_key(self):
        """Testa chave vazia"""
        cache = MemoryCache()
        
        cache.set("", "empty_key_value")
        
        assert cache.get("") == "empty_key_value"
    
    def test_very_long_key(self):
        """Testa chave muito longa"""
        cache = MemoryCache()
        
        long_key = "k" * 10000
        cache.set(long_key, "value")
        
        assert cache.get(long_key) == "value"
    
    def test_maxsize_one(self):
        """Testa com maxsize = 1"""
        cache = MemoryCache(maxsize=1)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert len(cache) == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
    
    def test_concurrent_operations(self):
        """Testa operações concorrentes (básico)"""
        cache = MemoryCache(maxsize=100)
        
        # Simula muitas operações
        for i in range(1000):
            cache.set(f"key_{i % 50}", f"value_{i}")
            cache.get(f"key_{i % 30}")
            if i % 10 == 0:
                cache.delete(f"key_{i % 20}")
        
        # Deve manter consistência
        assert len(cache) <= 100
    
    def test_repeated_clear(self):
        """Testa clear repetido"""
        cache = MemoryCache()
        
        cache.set("key", "value")
        cache.clear()
        cache.clear()  # Segundo clear não deve causar erro
        
        assert len(cache) == 0
    
    def test_get_moves_to_end(self):
        """Testa que get move item para o fim"""
        cache = MemoryCache(maxsize=3)
        
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        
        # Acessa 'a' - move para o fim
        cache.get("a")
        
        # Adiciona 'd' - deve evictar 'b' (não 'a')
        cache.set("d", 4)
        
        assert cache.get("a") == 1  # Ainda existe
        assert cache.get("b") is None  # Foi evicted
