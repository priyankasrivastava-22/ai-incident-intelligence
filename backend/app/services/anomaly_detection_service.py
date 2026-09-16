from statistics import mean, pstdev

class AnomalyDetectionService:
    # Detect whether the latest signal is above the historical baseline.
    def detect_error_rate_anomaly(self, error_counts: list[int], threshold: float = 2.0) -> dict:
        if len(error_counts) < 2:
            return {"is_anomaly": False, "score": 0.0, "baseline": 0.0, "current": error_counts[-1] if error_counts else 0}
        baseline_values = error_counts[:-1]
        current = error_counts[-1]
        baseline = mean(baseline_values)
        deviation = pstdev(baseline_values)
        if deviation == 0:
            score = float("inf") if current > baseline else 0.0
        else:
            score = (current - baseline) / deviation
        return {
            "is_anomaly": score >= threshold,
            "score": score,
            "baseline": baseline,
            "current": current,
        }