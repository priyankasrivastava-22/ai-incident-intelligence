from backend.app.services.anomaly_detection_service import AnomalyDetectionService

def test_error_rate_anomaly():
    service = AnomalyDetectionService()
    result = service.detect_error_rate_anomaly([2, 3, 2, 3, 15])
    assert result["is_anomaly"] is True
    assert result["current"] == 15
    assert result["baseline"] == 2.5

def test_normal_error_rate():
    service = AnomalyDetectionService()
    result = service.detect_error_rate_anomaly([2, 3, 2, 3, 3])
    assert result["is_anomaly"] is False
    assert result["current"] == 3