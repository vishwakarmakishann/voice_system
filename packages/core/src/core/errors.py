class PlatformError(Exception):
    """Base exception for all platform errors."""
    pass

class ProviderError(PlatformError):
    """Base exception for provider-related errors."""
    pass

class STTProviderError(ProviderError):
    pass

class LLMProviderError(ProviderError):
    pass

class TTSProviderError(ProviderError):
    pass

class InterruptionError(PlatformError):
    """Raised when an operation is interrupted by the user speaking."""
    pass

class RecoverableError(PlatformError):
    """Errors that the system can automatically recover from."""
    pass

class CriticalError(PlatformError):
    """Errors requiring session termination."""
    pass
