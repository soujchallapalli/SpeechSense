from speechsense.data.base_mongo import BaseMongoRepository


class ProcessedRepository(BaseMongoRepository):
    def __init__(self) -> None:
        # Automatically targets the "ProcessedTranscript" collection
        super().__init__(collection_name="ProcessedTranscript")
