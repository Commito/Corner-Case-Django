from rest_framework_tracking.mixins import LoggingMixin


class ConfiguredLoggingMixin(LoggingMixin):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']

    def should_log(self, request, response):
        return request.method in self.logging_methods \
               or response.status_code >= 400
