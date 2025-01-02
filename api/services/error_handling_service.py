class ErrorHandlingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_logger = PerformanceLogger()
        self.error_metrics = ErrorMetricsCollector()
        self.alert_manager = AlertManager()

    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        error_type: str,
        severity: str = "medium",
    ) -> Dict[str, Any]:
        try:
            # Log error metrics
            await self.error_metrics.collect_error(error, error_type)

            # Send alerts for high severity errors
            if severity == "high":
                await self.alert_manager.send_alert(error, context)

        except Exception as e:
            self.logger.error(f"Error handling error: {str(e)}")
            raise

    def _format_error_response(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "error_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "stack_trace": self._get_formatted_stack_trace(error),
            "frequency": await self.error_metrics.get_frequency(type(error).__name__),
            "system_state": self._get_system_state(),
        }
