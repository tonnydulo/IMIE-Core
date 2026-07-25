from imie.services import AnalysisPipeline


def test_pipeline_can_be_created() -> None:
    pipeline = AnalysisPipeline()

    assert pipeline.trend_analyst is not None
    assert pipeline.lifecycle_engine is not None
    assert pipeline.acceptance_analyst is not None
    assert pipeline.risk_analyst is not None
    assert pipeline.decision_director is not None