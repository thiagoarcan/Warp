"""
Encoding Detection - Detecção automática de encoding de arquivos

Detecta o encoding de arquivos de texto usando múltiplas estratégias:
- chardet/charset_normalizer para detecção probabilística
- BOM (Byte Order Mark) para arquivos Unicode
- Heurísticas baseadas em padrões comuns
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from platform_base.utils.logging import get_logger

logger = get_logger(__name__)


# Encodings comuns para tentar em ordem de preferência
COMMON_ENCODINGS = [
    'utf-8',
    'utf-8-sig',  # UTF-8 com BOM
    'latin-1',    # ISO-8859-1
    'cp1252',     # Windows Latin-1
    'iso-8859-15', # Latin-9
    'utf-16',
    'utf-16-le',
    'utf-16-be',
    'ascii',
]

# BOMs conhecidos
BOM_MARKERS = {
    b'\xef\xbb\xbf': 'utf-8-sig',
    b'\xff\xfe': 'utf-16-le',
    b'\xfe\xff': 'utf-16-be',
    b'\x00\x00\xfe\xff': 'utf-32-be',
    b'\xff\xfe\x00\x00': 'utf-32-le',
}


def detect_bom(file_path: Path) -> Optional[str]:
    """
    Detecta encoding pelo BOM (Byte Order Mark)
    
    Args:
        file_path: Caminho para o arquivo
    
    Returns:
        Encoding detectado ou None
    """
    try:
        with open(file_path, 'rb') as f:
            raw_bytes = f.read(4)
        
        for bom, encoding in BOM_MARKERS.items():
            if raw_bytes.startswith(bom):
                logger.debug(f"BOM detected: {encoding}")
                return encoding
        
        return None
    except Exception as e:
        logger.warning(f"BOM detection failed: {e}")
        return None


def detect_with_chardet(file_path: Path, sample_size: int = 10000) -> Tuple[Optional[str], float]:
    """
    Detecta encoding usando chardet/charset_normalizer
    
    Args:
        file_path: Caminho para o arquivo
        sample_size: Número de bytes para analisar
    
    Returns:
        Tupla (encoding, confidence)
    """
    try:
        # Tentar charset_normalizer primeiro (mais moderno)
        try:
            from charset_normalizer.api import from_bytes
            
            with open(file_path, 'rb') as f:
                raw_bytes = f.read(sample_size)
            
            results = from_bytes(raw_bytes)
            if results:
                best_match = results.best()
                if best_match:
                    encoding = best_match.encoding
                    # charset_normalizer não retorna confidence diretamente
                    # mas podemos usar a presença de resultado como indicador
                    confidence = 0.9 if encoding else 0.0
                    logger.debug(f"charset_normalizer detected: {encoding}")
                    return encoding, confidence
        except ImportError:
            pass
        
        # Fallback para chardet
        try:
            import chardet
            
            with open(file_path, 'rb') as f:
                raw_bytes = f.read(sample_size)
            
            result = chardet.detect(raw_bytes)
            if result is not None:
                encoding = result.get('encoding')
                confidence = result.get('confidence', 0.0)
                
                logger.debug(f"chardet detected: {encoding}, confidence={confidence}")
                return encoding, confidence
            else:
                return None, 0.0
        except ImportError:
            logger.warning("Neither charset_normalizer nor chardet available")
            return None, 0.0
            
    except Exception as e:
        logger.warning(f"Charset detection failed: {e}")
        return None, 0.0


def detect_by_trial(file_path: Path) -> Optional[str]:
    """
    Detecta encoding tentando abrir o arquivo com diferentes encodings
    
    Args:
        file_path: Caminho para o arquivo
    
    Returns:
        Primeiro encoding que funciona ou None
    """
    for encoding in COMMON_ENCODINGS:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # Tentar ler primeiras linhas
                for _ in range(100):
                    line = f.readline()
                    if not line:
                        break
            
            logger.debug(f"Trial encoding success: {encoding}")
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            logger.debug(f"Trial encoding {encoding} failed: {e}")
            continue
    
    return None


def detect_encoding(file_path: str | Path, 
                    sample_size: int = 10000,
                    min_confidence: float = 0.7) -> str:
    """
    Detecta automaticamente o encoding de um arquivo
    
    Estratégia:
    1. Verifica BOM
    2. Usa chardet/charset_normalizer se disponível
    3. Tenta encodings comuns por força bruta
    4. Retorna UTF-8 como fallback
    
    Args:
        file_path: Caminho para o arquivo
        sample_size: Bytes para análise (default 10KB)
        min_confidence: Confiança mínima para aceitar resultado de chardet
    
    Returns:
        Nome do encoding detectado
    
    Example:
        >>> encoding = detect_encoding("dados.csv")
        >>> df = pd.read_csv("dados.csv", encoding=encoding)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.warning(f"File not found for encoding detection: {file_path}")
        return 'utf-8'
    
    # 1. Verificar BOM
    bom_encoding = detect_bom(file_path)
    if bom_encoding:
        logger.info(f"Encoding detected via BOM: {bom_encoding}")
        return bom_encoding
    
    # 2. Usar chardet/charset_normalizer
    chardet_encoding, confidence = detect_with_chardet(file_path, sample_size)
    if chardet_encoding and confidence >= min_confidence:
        # Normalizar nome do encoding
        encoding = chardet_encoding.lower()
        
        # Corrigir alguns nomes comuns
        encoding_map = {
            'iso-8859-1': 'latin-1',
            'windows-1252': 'cp1252',
            'windows-1250': 'cp1250',
        }
        encoding = encoding_map.get(encoding, encoding)
        
        logger.info(f"Encoding detected via chardet: {encoding} (confidence={confidence:.2%})")
        return encoding
    
    # 3. Tentar encodings por força bruta
    trial_encoding = detect_by_trial(file_path)
    if trial_encoding:
        logger.info(f"Encoding detected via trial: {trial_encoding}")
        return trial_encoding
    
    # 4. Fallback para UTF-8
    logger.info("Using fallback encoding: utf-8")
    return 'utf-8'


def get_encoding_info(file_path: str | Path, sample_size: int = 10000) -> dict:
    """
    Obtém informações detalhadas sobre o encoding de um arquivo
    
    Args:
        file_path: Caminho para o arquivo
        sample_size: Bytes para análise
    
    Returns:
        Dicionário com informações de encoding
    """
    file_path = Path(file_path)
    
    result = {
        'detected_encoding': None,
        'method': None,
        'confidence': 0.0,
        'has_bom': False,
        'bom_type': None,
        'chardet_result': None,
        'suggested_encoding': 'utf-8',
    }
    
    if not file_path.exists():
        return result
    
    # Verificar BOM
    bom_encoding = detect_bom(file_path)
    if bom_encoding:
        result['has_bom'] = True
        result['bom_type'] = bom_encoding
        result['detected_encoding'] = bom_encoding
        result['method'] = 'bom'
        result['confidence'] = 1.0
        result['suggested_encoding'] = bom_encoding
        return result
    
    # Chardet
    chardet_encoding, confidence = detect_with_chardet(file_path, sample_size)
    if chardet_encoding:
        result['chardet_result'] = {
            'encoding': chardet_encoding,
            'confidence': confidence
        }
        
        if confidence >= 0.7:
            result['detected_encoding'] = chardet_encoding
            result['method'] = 'chardet'
            result['confidence'] = confidence
            result['suggested_encoding'] = chardet_encoding
            return result
    
    # Trial
    trial_encoding = detect_by_trial(file_path)
    if trial_encoding:
        result['detected_encoding'] = trial_encoding
        result['method'] = 'trial'
        result['confidence'] = 0.5
        result['suggested_encoding'] = trial_encoding
        return result
    
    # Fallback
    result['method'] = 'fallback'
    result['suggested_encoding'] = 'utf-8'
    
    return result
