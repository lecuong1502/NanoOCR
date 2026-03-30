from fastapi import HTTPException, status

class DocumentNotFoundException(HTTPException):
    def __init__(self, document_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

class OcrResultNotFoundException(HTTPException):
    def __init__(self, document_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OCR result for document '{document_id}' not found.",
        )

class UnsupportedFileTypeException(HTTPException):
    def __init__(self, extension: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type '{extension}' is not supported.",
        )

class FileTooLargeException(HTTPException):
    def __init__(self, max_mb: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {max_mb} MB.",
        )

class OcrProcessingException(HTTPException):
    def __init__(self, detail: str = "OCR processing failed."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )

class StorageException(HTTPException):
    def __init__(self, detail: str = "File storage operation failed."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )