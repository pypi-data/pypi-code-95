from pydantic import BaseModel, Field

__all__ = ["PhpCompileResult"]


class PhpCompileResult(BaseModel):
    version: str = Field(..., title="PHP版本")
    time: float = Field(..., title="编译耗时", description="PHP 编译耗时")
