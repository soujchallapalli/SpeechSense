from speechsense.database.base_mongo import BaseMongoRepository


class ReportRepository(BaseMongoRepository):
    def __init__(self) -> None:
        # Automatically targets the "Report" collection
        super().__init__(collection_name="Report")
