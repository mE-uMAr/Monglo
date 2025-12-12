
from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession

class TransactionManager:
    
    def __init__(self, client: AsyncIOMotorClient):
        self.client = client
    
    async def transaction(self):
        session = await self.client.start_session()
        
        try:
            async with session.start_transaction():
                yield session
        finally:
            await session.end_session()
    
    async def execute_in_transaction(
        self,
        operations: list[Callable],
        *args,
        **kwargs
    ) -> list[Any]:
        async with await self.transaction() as session:
            results = []
            for operation in operations:
                result = await operation(session, *args, **kwargs)
                results.append(result)
            return results
    
    async def with_retry(
        self,
        operation: Callable,
        max_retries: int = 3
    ) -> Any:
        from pymongo.errors import PyMongoError
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await operation()
            except PyMongoError as e:
                last_error = e
                if not self._is_transient_error(e):
                    raise
                
                if attempt == max_retries - 1:
                    raise
                
                # Wait before retry (exponential backoff)
                import asyncio
                await asyncio.sleep(0.1 * (2 ** attempt))
        
        raise last_error
    
    def _is_transient_error(self, error: Exception) -> bool:
        error_codes = [
            112,  # WriteConflict
            117,  # CappedPositionLost  
            262,  # ExceededTimeLimit
            11600, # InterruptedAtShutdown
            11602, # InterruptedDueToReplStateChange
        ]
        
        if hasattr(error, 'code') and error.code in error_codes:
            return True
        
        error_msg = str(error).lower()
        transient_keywords = [
            'transient',
            'temporary',
            'timeout',
            'interrupted'
        ]
        
        return any(keyword in error_msg for keyword in transient_keywords)
