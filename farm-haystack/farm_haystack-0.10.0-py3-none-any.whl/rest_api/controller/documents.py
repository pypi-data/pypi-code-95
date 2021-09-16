from files import INDEXING_PIPELINE


@router.post("/documents")
def delete_document(
    index: Optional[str],
    filters: Optional[dict] = None
):
    if not INDEXING_PIPELINE:
        raise HTTPException(status_code=501, detail="Indexing Pipeline is not configured.")

    INDEXING_PIPELINE.get_document_store().delete_documents(index=index, filters=filters)

