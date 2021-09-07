from pydantic import BaseModel


class HTTPException(BaseModel):
    """
    A representation of an error, detail about the cause of the error will be
    provided on the `detail` field.

    """

    detail: str

    class Config:
        schema_extra = {
            'example': {
                'detail': 'Detail will be given about the error which has occurred'
            }
        }


BadRequestResponse = {
    'model': HTTPException,
    'description': 'The request is invalid',
}


NotFoundResponse = {
    'model': HTTPException,
    'description': 'The specified resource could not be found',
}
