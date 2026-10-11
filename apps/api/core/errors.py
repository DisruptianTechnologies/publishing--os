class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, retryable: bool = False, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        self.details = details or {}
        super().__init__(self.message)

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(code="NOT_FOUND", message=message, status_code=404, details=details)

class ForbiddenError(AppException):
    def __init__(self, message: str = "Access forbidden", details: dict = None):
        super().__init__(code="FORBIDDEN", message=message, status_code=403, details=details)

class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict", details: dict = None):
        super().__init__(code="CONFLICT", message=message, status_code=409, details=details)

class PolicyBlockedError(AppException):
    def __init__(self, message: str = "Action blocked by policy", details: dict = None):
        super().__init__(code="POLICY_BLOCKED", message=message, status_code=403, details=details)

class BudgetExceededError(AppException):
    def __init__(self, message: str = "Budget exceeded", details: dict = None):
        super().__init__(code="BUDGET_EXCEEDED", message=message, status_code=402, details=details)

class ApprovalRequiredError(AppException):
    def __init__(self, message: str = "Approval required", details: dict = None):
        super().__init__(code="APPROVAL_REQUIRED", message=message, status_code=409, details=details)

class RetryableError(AppException):
    def __init__(self, code: str, message: str, details: dict = None):
        super().__init__(code=code, message=message, status_code=500, retryable=True, details=details)

class NonRetryableError(AppException):
    def __init__(self, code: str, message: str, details: dict = None):
        super().__init__(code=code, message=message, status_code=500, retryable=False, details=details)
