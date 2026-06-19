from speechsense.data.base_mongo import BaseMongoRepository


class TranscriptRepository(BaseMongoRepository):
    def __init__(self) -> None:
        # Automatically targets the "Transcript" collection
        super().__init__(collection_name="Transcript")
